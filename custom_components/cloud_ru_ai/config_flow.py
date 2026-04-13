"""Config flow for Cloud.ru Foundation Models integration."""

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

from types import MappingProxyType
from typing import Any

import openai
import voluptuous as vol
from homeassistant.config_entries import (SOURCE_USER, ConfigEntry, ConfigFlow,
                                          ConfigFlowResult, ConfigSubentryFlow,
                                          SubentryFlowResult)
from homeassistant.const import CONF_API_KEY, CONF_LLM_HASS_API
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (NumberSelector,
                                            NumberSelectorConfig,
                                            SelectOptionDict, SelectSelector,
                                            SelectSelectorConfig,
                                            SelectSelectorMode,
                                            TemplateSelector)

from .const import (CLIENT_API_KEY, CLIENT_BASE_URI, CLIENT_PROJECT_ID,
                    CONF_CHAT_MODEL, CONF_MAX_TOKENS,
                    CONF_NO_HA_DEFAULT_PROMPT, CONF_PROJECT_ID, CONF_PROMPT,
                    CONF_RECOMMENDED, CONF_TEMPERATURE, CONF_THINKING_MODE,
                    CONF_TOP_P, DEFAULT_CHAT_MODEL,
                    DEFAULT_INSTRUCTIONS_PROMPT_RU,
                    DEFAULT_NO_HA_DEFAULT_PROMPT, DEFAULT_THINKING_MODE,
                    DOC_API_KEY_GUIDE_URL, DOC_PROJECT_ID_GUIDE_URL, DOMAIN,
                    LOGGER, RECOMMENDED_CONVERSATION_OPTIONS,
                    RECOMMENDED_MAX_TOKENS, RECOMMENDED_TEMPERATURE,
                    RECOMMENDED_TOP_P)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROJECT_ID): str,
        vol.Required(CONF_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect."""
    client = openai.AsyncOpenAI(
        api_key=data[CONF_API_KEY],
        http_client=get_async_client(hass),
        base_url=CLIENT_BASE_URI,
        default_headers={CLIENT_API_KEY: data[CONF_API_KEY], CLIENT_PROJECT_ID: data[CONF_PROJECT_ID]}
    )

    await client.with_options(timeout=10).models.list()


class CloudRUAIConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cloud.ru Foundation Models."""

    VERSION = 2
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "project_id_guide_url": DOC_PROJECT_ID_GUIDE_URL,
                    "api_key_guide_url": DOC_API_KEY_GUIDE_URL,
                },
            )

        errors: dict[str, str] = {}

        self._async_abort_entries_match(user_input)
        try:
            await validate_input(self.hass, user_input)
        except openai.APIConnectionError:
            errors["base"] = "cannot_connect"
        except openai.AuthenticationError:
            errors["base"] = "invalid_auth"
        except Exception:
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title="Cloud.ru Foundation Models",
                data=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

    @classmethod
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this handler."""
        return {
            "conversation": ConversationFlowHandler,
            "ai_task_data": AITaskDataFlowHandler,
        }


class ConversationFlowHandler(ConfigSubentryFlow):
    """Handle conversation subentry flow."""

    def __init__(self) -> None:
        """Initialize."""
        self.last_rendered_recommended = False
        self.options: dict[str, Any] | MappingProxyType[str, Any] = {}

    @property
    def _is_new(self) -> bool:
        """Return if this is a new subentry."""
        return self.source == "user"

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        """Create a new conversation subentry."""
        self.options = RECOMMENDED_CONVERSATION_OPTIONS.copy()
        self.last_rendered_recommended = self.options[CONF_RECOMMENDED]
        return await self.async_step_init(user_input)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        """Reconfigure an existing conversation subentry."""
        self.options = self._get_reconfigure_subentry().data.copy()
        self.last_rendered_recommended = self.options.get(CONF_RECOMMENDED, False)
        return await self.async_step_init(user_input)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        """Manage conversation subentry configuration."""

        if user_input is not None:
            recommended = user_input[CONF_RECOMMENDED]

            if recommended == self.last_rendered_recommended:
                if not user_input.get(CONF_LLM_HASS_API):
                    user_input.pop(CONF_LLM_HASS_API, None)

                if self._is_new:
                    return self.async_create_entry(
                        title=user_input.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL),
                        data=user_input,
                    )
                return self.async_update_and_abort(
                    self._get_entry(),
                    self._get_reconfigure_subentry(),
                    data=user_input,
                )

            # Re-render with recommended toggle changed
            self.last_rendered_recommended = recommended
            self.options = dict(user_input)

        # Fetch models
        client: openai.AsyncOpenAI = self._get_entry().runtime_data
        model_options: list[SelectOptionDict] | None = None
        try:
            response = await client.models.list()
            model_options = []
            for model in response.data:
                if model.metadata.get("type") != "llm":  # type: ignore[attr-defined]
                    continue

                is_billable = model.metadata.get("is_billable", True)  # type: ignore[attr-defined]
                billable_emoji = "🆓" if not is_billable else "💰"

                tools_emoji = " 🔧" if getattr(model, "function_calling", False) else ""

                label = f"{model.id} {billable_emoji}{tools_emoji}"

                model_options.append(SelectOptionDict(label=label, value=model.id))
        except Exception:
            LOGGER.exception("Failed to fetch models, falling back to text input")

        schema = cloud_ru_ai_config_option_schema(self.hass, self.options, model_options)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "project_id_guide_url": DOC_PROJECT_ID_GUIDE_URL,
                "api_key_guide_url": DOC_API_KEY_GUIDE_URL,
            }
        )


class AITaskDataFlowHandler(ConfigSubentryFlow):
    """Handle AI task subentry flow."""

    def __init__(self) -> None:
        """Initialize."""
        self.options: dict[str, Any] = {}
        self.models: dict[str, str] = {}

    @property
    def _is_new(self) -> bool:
        """Return if this is a new subentry."""
        return self.source == SOURCE_USER

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to create an AI task."""
        self.options = {}
        return await self.async_step_init(user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle reconfiguration of an AI task."""
        self.options = self._get_reconfigure_subentry().data.copy()
        return await self.async_step_init(user_input)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to create / reconfigure AI task."""

        if user_input is not None:
            model_id = user_input[CONF_CHAT_MODEL]
            title = self.models.get(model_id, model_id)
            if self._is_new:
                return self.async_create_entry(title=title, data=user_input)
            return self.async_update_and_abort(
                self._get_entry(),
                self._get_reconfigure_subentry(),
                data=user_input,
            )

        # Fetch models
        client: openai.AsyncOpenAI = self._get_entry().runtime_data
        model_options: list[SelectOptionDict] = []
        self.models = {}
        try:
            response = await client.models.list()
            for model in response.data:
                if model.metadata.get("type") != "llm":  # type: ignore[attr-defined]
                    continue

                if not getattr(model, "structure_output", False):
                    continue

                is_billable = model.metadata.get("is_billable", True)  # type: ignore[attr-defined]
                billable_emoji = "🆓" if not is_billable else "💰"

                label = f"{model.id} {billable_emoji}"

                model_options.append(SelectOptionDict(label=label, value=model.id))
                self.models[model.id] = label
        except Exception:
            LOGGER.exception("Failed to fetch models for AI Task")
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CHAT_MODEL, default=self.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=model_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )


def cloud_ru_ai_config_option_schema(
    hass: HomeAssistant,
    options: dict[str, Any] | MappingProxyType[str, Any],
    model_options: list[SelectOptionDict] | None = None,
) -> dict:
    """Return a schema for Cloud.ru Foundation Models completion options."""

    hass_apis: list[SelectOptionDict] = [
        SelectOptionDict(label=api.name, value=api.id)
        for api in llm.async_get_apis(hass)
    ]

    chat_model_selector = str if not model_options else SelectSelector(
        SelectSelectorConfig(mode=SelectSelectorMode.DROPDOWN, options=model_options)
    )

    schema = {
        vol.Optional(
            CONF_PROMPT,
            description={"suggested_value": options.get(CONF_PROMPT, DEFAULT_INSTRUCTIONS_PROMPT_RU)},
        ): TemplateSelector(),
        vol.Optional(
            CONF_CHAT_MODEL,
            description={"suggested_value": options.get(CONF_CHAT_MODEL)},
            default=DEFAULT_CHAT_MODEL,
        ): chat_model_selector,
        vol.Optional(
            CONF_LLM_HASS_API,
            description={"suggested_value": options.get(CONF_LLM_HASS_API, [])},
        ): SelectSelector(
            SelectSelectorConfig(
                options=hass_apis,
                multiple=True,
                translation_key=CONF_LLM_HASS_API,
            )
        ),
        vol.Required(CONF_RECOMMENDED, default=options.get(CONF_RECOMMENDED, False)): bool,
    }

    if options.get(CONF_RECOMMENDED):
        return schema

    schema.update(
        {
            vol.Optional(
                CONF_MAX_TOKENS,
                description={"suggested_value": options.get(CONF_MAX_TOKENS)},
                default=RECOMMENDED_MAX_TOKENS,
            ): int,
            vol.Optional(
                CONF_TOP_P,
                description={"suggested_value": options.get(CONF_TOP_P)},
                default=RECOMMENDED_TOP_P,
            ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
            vol.Optional(
                CONF_TEMPERATURE,
                description={"suggested_value": options.get(CONF_TEMPERATURE)},
                default=RECOMMENDED_TEMPERATURE,
            ): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.05)),
            vol.Optional(
                CONF_THINKING_MODE,
                description={"suggested_value": options.get(CONF_THINKING_MODE, DEFAULT_THINKING_MODE)},
                default=options.get(CONF_THINKING_MODE, DEFAULT_THINKING_MODE),
            ): bool,
            vol.Optional(
                CONF_NO_HA_DEFAULT_PROMPT,
                description={"suggested_value": options.get(CONF_NO_HA_DEFAULT_PROMPT, DEFAULT_NO_HA_DEFAULT_PROMPT)},
                default=options.get(CONF_NO_HA_DEFAULT_PROMPT, DEFAULT_NO_HA_DEFAULT_PROMPT),
            ): bool,
        }
    )

    return schema
