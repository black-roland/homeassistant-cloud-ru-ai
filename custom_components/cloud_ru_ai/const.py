"""Constants for the Cloud.ru Foundation Models integration."""

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

import logging

DOMAIN = "cloud_ru_ai"
LOGGER = logging.getLogger(__package__)

CLIENT_BASE_URI = "https://foundation-models.api.cloud.ru/v1"
CLIENT_API_KEY = "x-api-key"
CLIENT_PROJECT_ID = "x-project-id"

CONF_PROJECT_ID = "project_id"
CONF_PROMPT = "prompt"
CONF_RECOMMENDED = "recommended"
CONF_MAX_TOKENS = "max_tokens"
CONF_CHAT_MODEL = "chat_model"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"
CONF_NO_HA_DEFAULT_PROMPT = "no_ha_default_prompt"

RECOMMENDED_MAX_TOKENS = 1024
RECOMMENDED_TEMPERATURE = 0.5
RECOMMENDED_TOP_P = 0.5

DEFAULT_CHAT_MODEL = "MiniMaxAI/MiniMax-M2"
DEFAULT_INSTRUCTIONS_PROMPT_RU = """Ты — голосовой ассистент для Home Assistant.
Отвечай на вопросы правдиво. Отвечай кратко, чётко и на русском языке.
"""
DEFAULT_NO_HA_DEFAULT_PROMPT = False
