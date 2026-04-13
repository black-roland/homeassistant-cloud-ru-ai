"""Base entity for Cloud.ru Foundation Models."""

# Copyright 2023-2025 @home-assistant contributors
# Copyright 2026 @black-roland and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Callable
from typing import TYPE_CHECKING, Any

import openai
import voluptuous as vol
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigSubentry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import llm
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.json import json_dumps
from openai._types import NOT_GIVEN
from openai.types.chat import (ChatCompletionAssistantMessageParam,
                               ChatCompletionMessage,
                               ChatCompletionMessageFunctionToolCallParam,
                               ChatCompletionMessageParam,
                               ChatCompletionSystemMessageParam,
                               ChatCompletionToolMessageParam,
                               ChatCompletionToolParam,
                               ChatCompletionUserMessageParam)
from openai.types.chat.chat_completion_message_function_tool_call_param import \
    Function
from openai.types.shared_params import (FunctionDefinition,
                                        ResponseFormatJSONSchema)
from openai.types.shared_params.response_format_json_schema import JSONSchema
from voluptuous_openapi import convert

from . import CloudRUAIConfigEntry
from .const import (CONF_CHAT_MODEL, CONF_MAX_TOKENS, CONF_TEMPERATURE,
                    CONF_THINKING_MODE, CONF_TOP_P, DEFAULT_CHAT_MODEL,
                    DEFAULT_THINKING_MODE, DOMAIN, LOGGER,
                    RECOMMENDED_MAX_TOKENS, RECOMMENDED_TEMPERATURE,
                    RECOMMENDED_TOP_P)

MAX_TOOL_ITERATIONS = 10


def _adjust_schema(schema: dict[str, Any]) -> None:
    """Adjust the schema to be compatible with the API."""

    # Remove empty enum arrays that cause compilation errors
    if "enum" in schema and (not schema["enum"] or schema["enum"] == []):
        del schema["enum"]

    if schema.get("type") == "object":
        if "properties" not in schema:
            return
        if "required" not in schema:
            schema["required"] = []
        for prop, prop_info in schema["properties"].items():
            _adjust_schema(prop_info)
            if prop not in schema["required"]:
                prop_info["type"] = [prop_info["type"], "null"]
                schema["required"].append(prop)
    elif schema.get("type") == "array":
        if "items" in schema:
            _adjust_schema(schema["items"])


def _format_structured_output(
    name: str, schema: vol.Schema, llm_api: llm.APIInstance | None
) -> JSONSchema:
    """Format the schema to be compatible with Cloud.ru API."""
    result: JSONSchema = {"name": name, "strict": True}
    result_schema = convert(
        schema,
        custom_serializer=llm_api.custom_serializer if llm_api else llm.selector_serializer,
    )
    _adjust_schema(result_schema)
    result["schema"] = result_schema
    return result


def _format_tool(
    tool: llm.Tool, custom_serializer: Callable[[Any], Any] | None
) -> ChatCompletionToolParam:
    """Format tool specification (exact copy of your original)."""
    params = convert(tool.parameters, custom_serializer=custom_serializer)

    if not tool.parameters.schema:
        params = {"type": "object", "properties": {}, "additionalProperties": False}
    elif params.get("type") == "object":
        required = params.get("required")
        if required in (None, {}, []) or (isinstance(required, list) and not required):
            params.pop("required", None)
        elif isinstance(required, dict):
            params["required"] = list(required.keys())
        elif not isinstance(required, list):
            params["required"] = list(required) if required else []

    tool_spec = FunctionDefinition(name=tool.name, parameters=params)
    if tool.description:
        tool_spec["description"] = tool.description
    return {"type": "function", "function": tool_spec}


def _convert_content_to_chat_message(
    content: conversation.Content, system_prompt_override: str | None = None
) -> ChatCompletionMessageParam | None:
    """Convert HA content → OpenAI format (supports no_ha_default_prompt override)."""
    if isinstance(content, conversation.ToolResultContent):
        return ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=content.tool_call_id,
            content=json_dumps(content.tool_result),
        )

    if content.role == "system" and content.content:
        text = system_prompt_override if system_prompt_override is not None else content.content
        return ChatCompletionSystemMessageParam(role="system", content=text)

    if content.role == "user" and content.content:
        return ChatCompletionUserMessageParam(role="user", content=content.content)

    if content.role == "assistant":
        param = ChatCompletionAssistantMessageParam(role="assistant", content=content.content)
        if isinstance(content, conversation.AssistantContent) and content.tool_calls:
            param["tool_calls"] = [
                ChatCompletionMessageFunctionToolCallParam(
                    type="function",
                    id=tool_call.id,
                    function=Function(
                        arguments=json_dumps(tool_call.tool_args),
                        name=tool_call.tool_name,
                    ),
                )
                for tool_call in content.tool_calls
            ]
        return param

    LOGGER.warning("Could not convert message: %s", content)
    return None


async def _transform_response(
    message: ChatCompletionMessage,
) -> AsyncGenerator[conversation.AssistantContentDeltaDict, None]:
    """Transform non-stream response (used by AI Task)."""
    data: conversation.AssistantContentDeltaDict = {
        "role": message.role,
        "content": message.content,
    }
    if message.tool_calls:
        data["tool_calls"] = [
            llm.ToolInput(
                id=tool_call.id,
                tool_name=tool_call.function.name,
                tool_args=json.loads(tool_call.function.arguments),
            )
            for tool_call in message.tool_calls
            if tool_call.type == "function"
        ]
    yield data


class CloudRUAIEntity(Entity):
    """Shared base entity."""

    _attr_has_entity_name = True

    def __init__(self, entry: CloudRUAIConfigEntry, subentry: ConfigSubentry) -> None:
        """Initialize shared entity."""
        self.entry = entry
        self.subentry = subentry
        self.model = subentry.data.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            manufacturer="Cloud.ru",
            model="Foundation Models",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    async def _async_handle_chat_log(
        self,
        chat_log: conversation.ChatLog,
        structure_name: str | None = None,
        structure: vol.Schema | None = None,
    ) -> None:
        """Non-streaming chat completion (used by AI Task + structured output)."""
        options = self.subentry.data
        model = options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)

        tools = None
        if chat_log.llm_api:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]

        model_args: dict[str, Any] = {
            "model": model,
            "messages": [m for content in chat_log.content if (m := _convert_content_to_chat_message(content))],
            "tools": tools or NOT_GIVEN,
            "tool_choice": "auto" if tools else "none",
            "parallel_tool_calls": False,
            "max_completion_tokens": options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS),
            "top_p": options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
            "temperature": options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE),
            "user": chat_log.conversation_id,
        }

        if structure:
            if TYPE_CHECKING:
                assert structure_name is not None
            model_args["response_format"] = ResponseFormatJSONSchema(
                type="json_schema",
                json_schema=_format_structured_output(structure_name, structure, chat_log.llm_api),
            )

        # Cloud.ru thinking mode (default off for AI Task)
        if not options.get(CONF_THINKING_MODE, DEFAULT_THINKING_MODE):
            model_args["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

        client = self.entry.runtime_data

        for _iteration in range(MAX_TOOL_ITERATIONS):
            try:
                result = await client.chat.completions.create(**model_args)
            except openai.OpenAIError as err:
                LOGGER.exception("Error talking to Cloud.ru API")
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="api_error",
                    translation_placeholders={"details": str(err)},
                ) from err

            if not result.choices:
                raise HomeAssistantError("API returned empty response")

            result_message = result.choices[0].message

            model_args["messages"].extend(
                [
                    msg
                    async for content in chat_log.async_add_delta_content_stream(
                        self.entity_id, _transform_response(result_message)
                    )
                    if (msg := _convert_content_to_chat_message(content))
                ]
            )

            if not chat_log.unresponded_tool_results:
                break
