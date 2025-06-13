See [description in English](#cloudru-foundation-models-for-home-assistant) below 👇
<br>
<br>

# Cloud.ru Foundation Models для Home Assistant

[![Добавить репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) [![Настроить интеграцию с Cloud.ru](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai)

Ассистент с искусственным интеллектом для вашего умного дома. Интеграция объединяет возможности [Cloud.ru Foundation Models](https://cloud.ru/marketplace/ai-ml) с Home Assistant, позволяя создать полноценную систему управления умным домом с естественным языковым интерфейсом.

## Возможности

- Общение с ассистентом через интерфейс Home Assistant.
- Управление через приложение Home Assistant.
- Поддержка различных задач, включая генерацию контента.

Cloud.ru Foundation Models — облачный сервис, плата за который взимается в соответствии с [тарифами](https://cloud.ru/docs/marketplace/ug/services/ai-playground/pricing__ai-playground).

## Установка и настройка

### Подготовка

1. Зарегистрируйтесь в [Cloud.ru](https://console.cloud.ru/registration/?zoneclick=github&retain_url=https://github.com/black-roland/homeassistant-cloud-ru-ai);
2. Получите [идентификатор проекта](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__project-id);
3. Зарегистрируйте [ключ API](https://cloud.ru/docs/console_api/ug/topics/guides__static-api-keys__create) с ролью `ml_inference_ai_marketplace`;
4. Сохраните полученные данные.

### Установка

1. [Скачайте интеграцию](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) через HACS;
2. Перезапустите Home Assistant;
3. Перейдите в **Настройки → Устройства и службы → Добавить интеграцию** или используйте [кнопку настройки](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai);
4. Введите **идентификатор проекта** и **ключ API**, полученные в личном кабинете Cloud.ru.

## Примеры использования

Примеры использования можно найти в [моем блоге](https://mansmarthome.info/tags/ai/) — все статьи про YandexGPT актуальны и для этой интеграции.

<p>
  <img src="https://github.com/user-attachments/assets/c4f2520d-a1e7-433b-99d6-9db29b2c99f1" height="340px" alt="Assist" />
  <img src="https://github.com/user-attachments/assets/34f05829-7a10-4087-8596-5087b8310533" height="340px" alt="Morning digests" />
</p>

## Поддержка автора

Если интеграция оказалась полезной, вы можете [угостить автора чашечкой кофе](https://mansmarthome.info/donate/#donationalerts). Ваша благодарность ценится!

#### Благодарности

Огромное спасибо всем, кто поддерживает этот проект:

![Спасибо][donors-list]

## Уведомление

Данная интеграция является неофициальной и не связана с Cloud.ru. Cloud.ru Foundation Models — это сервис, предоставляемый Cloud.ru.

Данная интеграция не является официальным продуктом Cloud.ru и не поддерживается Cloud.ru.

---

# Cloud.ru Foundation Models for Home Assistant

[![Add repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) [![Configure Cloud.ru Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai)

An AI-powered assistant for your smart home. This integration combines the capabilities of [Cloud.ru Foundation Models](https://cloud.ru/marketplace/ai-ml) with Home Assistant, enabling a full-fledged smart home control system with a natural language interface.

## Features

- Communicate with the assistant via the Home Assistant UI.
- Control via the Home Assistant app.
- Support for various tasks, including content generation.

Cloud.ru Foundation Models is a cloud service billed according to [pricing plans](https://cloud.ru/docs/marketplace/ug/services/ai-playground/pricing__ai-playground).

## Installation & Setup

### Preparation

1. Register on [Cloud.ru](https://console.cloud.ru/registration/?zoneclick=github&retain_url=https://github.com/black-roland/homeassistant-cloud-ru-ai);
2. Obtain a [project ID](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__project-id);
3. Generate an [API key](https://cloud.ru/docs/console_api/ug/topics/guides__static-api-keys__create) with the `ml_inference_ai_marketplace` role;
4. Save the obtained credentials.

### Installation

1. [Download the integration](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) via HACS;
2. Restart Home Assistant;
3. Go to **Settings → Devices & Services → Add Integration** or use the [configuration button](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai);
4. Enter the **project ID** and **API key** obtained from your Cloud.ru account.

## Donations

If you find this integration useful, you can [buy the author a cup of coffee](https://mansmarthome.info/donate/#donationalerts). Your appreciation is highly valued!

#### Thank you

A huge thank you to everyone supporting this project:

![Thank you][donors-list]

## Notice

This integration is unofficial and not affiliated with Cloud.ru. Cloud.ru Foundation Models is a service provided by Cloud.ru.

This integration is not an official Cloud.ru product and is not supported by Cloud.ru.

[donors-list]: https://github.com/user-attachments/assets/71f80a87-5c65-44e4-811a-14bb075caa9c
