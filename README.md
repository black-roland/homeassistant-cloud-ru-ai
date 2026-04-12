See [description in English](#cloudru-foundation-models-for-home-assistant) below 👇
<br>
<br>

# Cloud.ru Foundation Models для Home Assistant

[![Добавить репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) [![Настроить интеграцию с Cloud.ru](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai)

Интеллектуальный ассистент для вашего умного дома. Интеграция объединяет возможности [Cloud.ru Foundation Models](https://cloud.ru/products/evolution-foundation-models) с Home Assistant, позволяя создавать ассистентов на базе популярных открытых LLM.

## Возможности

- Общение с ИИ-ассистентом через интерфейс Home Assistant.
- Полноценное управление умным домом: ассистент может не только сообщать состояние устройств, но и управлять ими (включать свет, регулировать температуру и т.д.), а также запускать скрипты ([демо](https://boosty.to/mansmarthome/posts/bb1e2d91-6edb-4dfe-b96f-99de636ce844)).
- Доступ к популярным open source моделям: **MiniMax-M2**, **GLM-4.6**, **Qwen3-Coder-480B-A35B-Instruct**, **T-pro-it-2.0** и [другим](https://cloud.ru/products/evolution-ai-factory/catalog-foundation-models).
- Генерация текстового контента и ответов на вопросы.
- Легкое тестирование разных моделей прямо в Home Assistant.

Cloud.ru Foundation Models — облачный сервис, плата за который взимается в соответствии с [тарифами](https://cloud.ru/products/evolution-ai-factory/catalog-foundation-models).

## Установка и настройка

### Подготовка

1. Зарегистрируйтесь в [Cloud.ru](https://console.cloud.ru/registration/?zoneclick=github&retain_url=https://github.com/black-roland/homeassistant-cloud-ru-ai);
2. Получите [идентификатор проекта](https://cloud.ru/docs/administration/ug/topics/guides__projects#guides-projects-id);
3. Создайте [сервисный аккаунт и сгенерируйте для него ключ API](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__authentication);
4. Сохраните полученные данные.

### Установка

1. [Скачайте интеграцию](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) через HACS;
2. Перезапустите Home Assistant;
3. Перейдите в **Настройки → Устройства и службы → Добавить интеграцию** или используйте [кнопку настройки](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai);
4. Введите **идентификатор проекта** и **ключ API**, полученные в личном кабинете Cloud.ru.

## Примеры использования

Ищете идеи для вдохновения? В [моём блоге](https://mansmarthome.info/tags/ai/) можно найти парочку практических примеров работы с ИИ-ассистентами в Home Assistant. Все идеи из статей про [YandexGPT](https://github.com/black-roland/homeassistant-yandexgpt) легко адаптируются и для этой интеграции.

Хотите сравнить возможности? Обе интеграции предоставляют мощные ИИ-инструменты для Home Assistant, но с разными особенностями:

- Cloud.ru Foundation Models — доступ к открытым моделям (Llama, Qwen, T-Pro и другим).
- [YandexGPT](https://github.com/black-roland/homeassistant-yandexgpt) — интеграция проприетарной модели Яндекса с поддержкой генерации изображений.

Обе интеграции можно использовать для создания умных ассистентов, утренних дайджестов и других ИИ-функций в вашем умном доме.

<p>
  <img src="https://github.com/user-attachments/assets/0e590b9a-555a-45ec-a825-f583f7a7e079" height="400" alt="MCP" />
  <img src="https://github.com/user-attachments/assets/34f05829-7a10-4087-8596-5087b8310533" height="400" alt="Morning digests" />
</p>

## Поддержка автора

Если интеграция оказалась полезной, вы можете [угостить автора чашечкой кофе](https://mansmarthome.info/donate/?utm_source=github&utm_medium=referral&utm_campaign=cloudru#%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0-%D0%B1%D1%8B%D1%81%D1%82%D1%80%D1%8B%D1%85-%D0%BF%D0%BB%D0%B0%D1%82%D0%B5%D0%B6%D0%B5%D0%B9). Ваша благодарность ценится!

#### Благодарности

Огромное спасибо всем, кто поддерживает этот проект:

![Спасибо][donors-list]

## Уведомление

Данная интеграция является неофициальной и не связана с Cloud.ru. Cloud.ru Foundation Models — это сервис, предоставляемый Cloud.ru.

Данная интеграция не является официальным продуктом Cloud.ru и не поддерживается Cloud.ru. Разработчик интеграции не несёт ответственности за:
- Изменения в API Cloud.ru;
- Прекращение работы сервиса Cloud.ru Foundation Models;
- Любые возможные неполадки или убытки, вызванные использованием данной интеграции.

## Лицензия

Код распространяется под лицензией [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Интеграция основана на [коде компонента Home Assistant для OpenAI](https://www.home-assistant.io/integrations/openai_conversation/).

---

# Cloud.ru Foundation Models for Home Assistant

[![Add repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) [![Configure Cloud.ru Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai)

An intelligent assistant for your smart home. This integration combines the capabilities of [Cloud.ru Foundation Models](https://cloud.ru/products/evolution-foundation-models) with Home Assistant, allowing you to create assistants based on popular open-source LLMs.

## Features

- Communicate with the assistant via the Home Assistant UI.
- Full smart home control: assistant can not only report device states but also control them (turn lights on/off, adjust temperature etc.) and execute scripts ([demo](https://boosty.to/mansmarthome/posts/bb1e2d91-6edb-4dfe-b96f-99de636ce844)).
- Access to popular open source LLMs: **MiniMax-M2**, **GLM-4.6**, **Qwen3-Coder-480B-A35B-Instruct**, **T-pro-it-2.0** and [others](https://cloud.ru/products/evolution-foundation-models).
- Text content generation and question answering.
- Easy testing of different models directly in Home Assistant.

Cloud.ru Foundation Models is a cloud service billed according to [pricing plans](https://cloud.ru/docs/marketplace/ug/services/ai-playground/pricing__ai-playground).

## Installation & Setup

### Preparation

1. Register on [Cloud.ru](https://console.cloud.ru/registration/?zoneclick=github&retain_url=https://github.com/black-roland/homeassistant-cloud-ru-ai);
2. Obtain a [project ID](https://cloud.ru/docs/administration/ug/topics/guides__projects#guides-projects-id);
3. Create [a service account and generate an API key](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__authentication);
4. Save the obtained credentials.

### Installation

1. [Download the integration](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) via HACS;
2. Restart Home Assistant;
3. Go to **Settings → Devices & Services → Add Integration** or use the [configuration button](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai);
4. Enter the **project ID** and **API key** obtained from your Cloud.ru account.

## Donations

If you find this integration useful, you can [buy the author a cup of coffee](https://boosty.to/mansmarthome/donate?utm_source=github&utm_medium=referral&utm_campaign=cloudru). Your appreciation is highly valued!

#### Thank you

A huge thank you to everyone supporting this project:

![Thank you][donors-list]

## Notice

This integration is unofficial and not affiliated with Cloud.ru. Cloud.ru Foundation Models is a service provided by Cloud.ru.

This integration is not an official Cloud.ru product and is not supported by Cloud.ru. The integration developer is not responsible for:
- Cloud.ru API changes
- Cloud.ru Foundation Models service discontinuation
- Any potential issues or damages caused by using this integration

## License

The code is licensed under [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). The integration is based on the [Home Assistant OpenAI integration](https://www.home-assistant.io/integrations/openai_conversation/).

[donors-list]: https://github.com/user-attachments/assets/71f80a87-5c65-44e4-811a-14bb075caa9c
