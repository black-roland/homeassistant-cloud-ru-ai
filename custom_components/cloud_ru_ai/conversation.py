"""Conversation support for Cloud.ru Foundation Models."""

# Copyright 2023-2025 @home-assistant contributors
# Copyright 2025 @black-roland and contributors
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
from typing import Any, Literal, TypedDict, cast

import openai
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LLM_HASS_API, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, TemplateError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import intent, llm, template
from homeassistant.helpers.entity_platform import \
    AddConfigEntryEntitiesCallback
from openai._streaming import AsyncStream
from openai._types import NOT_GIVEN
from openai.types.chat import (ChatCompletionAssistantMessageParam,
                               ChatCompletionChunk,
                               ChatCompletionMessageFunctionToolCallParam,
                               ChatCompletionMessageParam,
                               ChatCompletionToolMessageParam,
                               ChatCompletionToolParam)
from openai.types.chat.chat_completion_message_function_tool_call_param import \
    Function
from openai.types.shared_params import FunctionDefinition
from voluptuous_openapi import convert

from . import CloudRUAIConfigEntry
from .const import (CONF_CHAT_MODEL, CONF_MAX_TOKENS,
                    CONF_NO_HA_DEFAULT_PROMPT, CONF_PROMPT, CONF_TEMPERATURE,
                    CONF_THINKING_MODE, CONF_TOP_P, DEFAULT_CHAT_MODEL,
                    DEFAULT_INSTRUCTIONS_PROMPT_RU,
                    DEFAULT_NO_HA_DEFAULT_PROMPT, DEFAULT_THINKING_MODE,
                    DOMAIN, LOGGER, RECOMMENDED_MAX_TOKENS,
                    RECOMMENDED_TEMPERATURE, RECOMMENDED_TOP_P)

# Max number of back and forth with the LLM to generate a response
MAX_TOOL_ITERATIONS = 10


class CurrentToolCall(TypedDict):
    index: int
    id: str
    tool_name: str
    tool_args: str


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: CloudRUAIConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    agent = CloudRUAIConversationEntity(config_entry)
    async_add_entities([agent])


def _format_tool(
    tool: llm.Tool, custom_serializer: Callable[[Any], Any] | None
) -> ChatCompletionToolParam:
    """Format tool specification."""
    params = convert(tool.parameters, custom_serializer=custom_serializer)

    # Patch for compatibility: handle "required" field (remove if empty)
    if not tool.parameters.schema:
        params = {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }
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
    return ChatCompletionToolParam(type="function", function=tool_spec)


def _convert_content_to_param(
        content: conversation.Content, system_prompt_override: str | None = None) -> ChatCompletionMessageParam:
    """Convert any native chat message for this agent to the native format."""
    if content.role == "tool_result":
        assert type(content) is conversation.ToolResultContent
        return ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=content.tool_call_id,
            content=json.dumps(content.tool_result),
        )
    if content.role != "assistant" or not content.tool_calls:
        text = content.content
        if content.role == "system" and system_prompt_override is not None:
            text = system_prompt_override
        return cast(ChatCompletionMessageParam, {"role": content.role, "content": text})

    # Handle the Assistant content including tool calls.
    assert type(content) is conversation.AssistantContent
    return ChatCompletionAssistantMessageParam(
        role="assistant",
        content=content.content,
        tool_calls=[
            ChatCompletionMessageFunctionToolCallParam(
                id=tool_call.id,
                function=Function(
                    arguments=json.dumps(tool_call.tool_args),
                    name=tool_call.tool_name,
                ),
                type="function",
            )
            for tool_call in content.tool_calls
        ],
    )


async def _transform_stream(
    result: AsyncStream[ChatCompletionChunk],
) -> AsyncGenerator[conversation.AssistantContentDeltaDict, None]:
    """Transform a Cloud.ru Foundation Models delta stream into HA format."""
    current_tool_call: CurrentToolCall | None = None

    async for chunk in result:
        LOGGER.debug("Received chunk: %s", chunk)

        # Treat empty choices as a finish reason.
        # Otherwise, `GetLiveContext` will fail with some models.
        # `GetLiveContext` is the only basic tool that doesn't take any
        # arguments — that might be the reason.
        if not chunk.choices or chunk.choices[0].finish_reason:
            if current_tool_call:
                yield {
                    "tool_calls": [
                        llm.ToolInput(
                            id=current_tool_call["id"],
                            tool_name=current_tool_call["tool_name"],
                            tool_args=json.loads(current_tool_call["tool_args"] or "{}"),
                        )
                    ]
                }

            break

        delta = chunk.choices[0].delta

        # Skip deltas with only whitespace (e.g., leading \n\n from some models)
        if current_tool_call is None and not delta.tool_calls:
            content = getattr(delta, "content", None)
            if content and not content.strip():  # Ignore if content is only whitespace
                continue
            yield {  # type: ignore[misc]
                key: value
                for key in ("role", "content")
                if (value := getattr(delta, key)) is not None
            }
            continue

        # When doing tool calls, we should always have a tool call
        # object or we have gotten stopped above with a finish_reason set.
        if (
            not delta.tool_calls
            or not (delta_tool_call := delta.tool_calls[0])
            or not delta_tool_call.function
        ):
            raise ValueError("Expected delta with tool call")

        if current_tool_call and delta_tool_call.index == current_tool_call["index"]:
            if current_tool_call is not None:
                current_tool_call["tool_args"] += delta_tool_call.function.arguments or ""
            continue

        # We got tool call with new index, so we need to yield the previous
        if current_tool_call:
            yield {
                "tool_calls": [
                    llm.ToolInput(
                        id=current_tool_call["id"],
                        tool_name=current_tool_call["tool_name"],
                        tool_args=json.loads(current_tool_call["tool_args"]),
                    )
                ]
            }

        current_tool_call = CurrentToolCall(
            index=delta_tool_call.index,
            id=cast(str, delta_tool_call.id),
            tool_name=cast(str, delta_tool_call.function.name),
            tool_args=delta_tool_call.function.arguments or "",
        )


class CloudRUAIConversationEntity(
    conversation.ConversationEntity
):
    """Cloud.ru Foundation Models conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supports_streaming = True

    def __init__(self, entry: CloudRUAIConfigEntry) -> None:
        """Initialize the agent."""
        self.entry = entry  # type: CloudRUAIConfigEntry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Cloud.ru",
            model="Foundation Models",
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        if self.entry.options.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Call the API."""
        options = self.entry.options

        system_prompt = options.get(CONF_PROMPT, DEFAULT_INSTRUCTIONS_PROMPT_RU)

        try:
            await chat_log.async_update_llm_data(
                DOMAIN,
                user_input,
                options.get(CONF_LLM_HASS_API),
                system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        tools: list[ChatCompletionToolParam] | None = None
        if chat_log.llm_api:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]

        no_ha_default_prompt = options.get(CONF_NO_HA_DEFAULT_PROMPT, DEFAULT_NO_HA_DEFAULT_PROMPT)
        system_prompt_override = await self._async_expand_prompt_template(
            system_prompt, user_input) if no_ha_default_prompt else None

        model = options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        messages = [_convert_content_to_param(content, system_prompt_override) for content in chat_log.content]

        client: openai.AsyncOpenAI = self.entry.runtime_data

        # To prevent infinite loops, we limit the number of iterations
        for _iteration in range(MAX_TOOL_ITERATIONS):
            model_args = {
                "model": model,
                "messages": messages,
                "tools": tools or NOT_GIVEN,
                "tool_choice": "auto" if tools else "none",
                "parallel_tool_calls": False,
                "max_completion_tokens": options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS),
                "top_p": options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
                "temperature": options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE),
                "user": chat_log.conversation_id,
                "stream": True,
                "stream_options": {
                    "include_usage": False,
                    "continuous_usage_stats": False,
                },
            }

            if not options.get(CONF_THINKING_MODE, DEFAULT_THINKING_MODE):
                model_args["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}  # vLLM option
                }

            try:
                result = await client.chat.completions.create(**model_args)
            except openai.RateLimitError as err:
                LOGGER.error("Rate limited by Cloud.ru Foundation Models API: %s", err)
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="rate_limited") from err
            except openai.OpenAIError as err:
                LOGGER.error("Error talking to Cloud.ru Foundation Models API: %s", err)
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="api_error") from err

            try:
                messages.extend(
                    [
                        _convert_content_to_param(content)
                        async for content in chat_log.async_add_delta_content_stream(
                            user_input.agent_id, _transform_stream(cast(AsyncStream[ChatCompletionChunk], result))
                        )
                    ]
                )
            except openai.OpenAIError as err:
                LOGGER.error("Error talking to Cloud.ru Foundation Models API: %s", err)
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="api_error") from err

            if not chat_log.unresponded_tool_results:
                break

        if not isinstance(chat_log.content[-1], conversation.AssistantContent):
            LOGGER.error("API did not return a valid assistant response")
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="no_assistant_response")

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(chat_log.content[-1].content or "")
        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=chat_log.continue_conversation,
        )

    async def _async_entry_update_listener(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        # Reload as we update device info + entity name + supported features
        await hass.config_entries.async_reload(entry.entry_id)

    async def _async_expand_prompt_template(
        self, prompt_template: str, user_input: conversation.ConversationInput
    ) -> str:
        """Render the prompt template."""
        try:
            system_prompt = template.Template(prompt_template, self.hass).async_render(parse_result=False)

            if user_input.extra_system_prompt:
                system_prompt += user_input.extra_system_prompt

            return system_prompt
        except TemplateError as err:
            raise HomeAssistantError("Error rendering prompt template") from err
