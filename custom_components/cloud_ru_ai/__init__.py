"""The Cloud.ru Foundation Models integration."""

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

import openai
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_API_KEY, CONF_LLM_HASS_API, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.httpx_client import get_async_client

from .const import (CLIENT_API_KEY, CLIENT_BASE_URI, CLIENT_PROJECT_ID,
                    CONF_PROJECT_ID, DOMAIN, LOGGER)

PLATFORMS = (Platform.CONVERSATION, Platform.AI_TASK)

type CloudRUAIConfigEntry = ConfigEntry[openai.AsyncOpenAI]  # type: ignore[name-defined]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:  # noqa: ARG001
    """Set up Cloud.ru Foundation Models."""
    await async_migrate_integration(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: CloudRUAIConfigEntry) -> bool:
    """Set up Cloud.ru Foundation Models from a config entry."""

    client = openai.AsyncOpenAI(
        api_key=entry.data[CONF_API_KEY],
        http_client=get_async_client(hass),
        base_url=CLIENT_BASE_URI,
        default_headers={CLIENT_API_KEY: entry.data[CONF_API_KEY], CLIENT_PROJECT_ID: entry.data[CONF_PROJECT_ID]},
    )

    # Cache current platform data which gets added to each request (caching done by library)
    _ = await hass.async_add_executor_job(client.platform_headers)

    try:
        await hass.async_add_executor_job(client.with_options(timeout=10.0).models.list)
    except openai.AuthenticationError as err:
        LOGGER.error("Invalid API key: %s", err)
        return False
    except openai.OpenAIError as err:
        raise ConfigEntryNotReady(err) from err

    entry.runtime_data = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload when subentry options change
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: CloudRUAIConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: CloudRUAIConfigEntry) -> bool:
    """Unload Cloud.ru Foundation Models."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_integration(hass: HomeAssistant) -> None:
    """Migrate old (v1) config entries to the new subentry structure."""
    entries = [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.version == 1]
    if not entries:
        return

    LOGGER.info("Migrating Cloud.ru Foundation Models to subentries (v2)")

    api_keys_entries: dict[tuple[str, str], tuple[CloudRUAIConfigEntry, bool]] = {}
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    for entry in entries:
        use_existing = False
        key = (entry.data[CONF_PROJECT_ID], entry.data[CONF_API_KEY])

        # Old single string / "none" → new list format
        options = dict(entry.options)
        if CONF_LLM_HASS_API in options:
            value = options[CONF_LLM_HASS_API]
            if isinstance(value, str):
                options[CONF_LLM_HASS_API] = [] if value == "none" else [value]

        subentry = ConfigSubentry(
            data=MappingProxyType(options),
            subentry_type="conversation",
            title=entry.title,
            unique_id=None,
        )

        if key not in api_keys_entries:
            use_existing = True
            all_disabled = all(
                e.disabled_by is not None for e in entries if (e.data[CONF_PROJECT_ID], e.data[CONF_API_KEY]) == key
            )
            api_keys_entries[key] = (entry, all_disabled)

        parent_entry, all_disabled = api_keys_entries[key]

        hass.config_entries.async_add_subentry(parent_entry, subentry)

        # Migrate conversation entity
        conversation_entity_id = entity_registry.async_get_entity_id("conversation", DOMAIN, entry.entry_id)
        device = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})

        if conversation_entity_id:
            conversation_entity_entry = entity_registry.entities[conversation_entity_id]
            entity_disabled_by = conversation_entity_entry.disabled_by
            if (entity_disabled_by is er.RegistryEntryDisabler.CONFIG_ENTRY and not all_disabled):
                entity_disabled_by = (er.RegistryEntryDisabler.DEVICE if device else er.RegistryEntryDisabler.USER)
            entity_registry.async_update_entity(
                conversation_entity_id,
                config_entry_id=parent_entry.entry_id,
                config_subentry_id=subentry.subentry_id,
                disabled_by=entity_disabled_by,
                new_unique_id=subentry.subentry_id,
            )

        # Migrate device
        if device:
            device_disabled_by = device.disabled_by
            if (device.disabled_by is dr.DeviceEntryDisabler.CONFIG_ENTRY and not all_disabled):
                device_disabled_by = dr.DeviceEntryDisabler.USER
            device_registry.async_update_device(
                device.id,
                disabled_by=device_disabled_by,
                new_identifiers={(DOMAIN, subentry.subentry_id)},
                add_config_subentry_id=subentry.subentry_id,
                add_config_entry_id=parent_entry.entry_id,
            )
            if parent_entry.entry_id != entry.entry_id:
                device_registry.async_update_device(
                    device.id, remove_config_entry_id=entry.entry_id
                )
            else:
                device_registry.async_update_device(
                    device.id,
                    remove_config_entry_id=entry.entry_id,
                    remove_config_subentry_id=None,
                )

        if not use_existing:
            await hass.config_entries.async_remove(entry.entry_id)
        else:
            hass.config_entries.async_update_entry(
                entry,
                title="Cloud.ru Foundation Models",
                options={},
                version=2,
                minor_version=2,
            )

    LOGGER.info("Migration to subentries completed successfully")


async def async_migrate_entry(hass: HomeAssistant, entry: CloudRUAIConfigEntry) -> bool:
    """Migrate config entry (for future versions)."""

    LOGGER.debug("Migrating from version %s.%s", entry.version, entry.minor_version)

    if entry.version > 2:
        return False

    hass.config_entries.async_update_entry(entry, version=2, minor_version=2)

    return True
