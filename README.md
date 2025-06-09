<div align="center">
  <h1>Cloud.ru Foundation Models для Home Assistant</h1>

  [![Добавить репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) [![Настроить интеграцию с Cloud.ru](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai)

  <p>Ассистент с искусственным интеллектом для вашего умного дома. Интеграция объединяет возможности Cloud.ru Foundation Models с Home Assistant, позволяя создать полноценную систему управления умным домом с естественным языковым интерфейсом.</p>
</div>

## Возможности

- Общение с ассистентом через интерфейс Home Assistant.
- Полное управление умным домом: ассистент может управлять устройствами, запускать автоматизации.
- Управление через приложение Home Assistant.
- Поддержка различных задач, включая генерацию контента.

Cloud.ru Foundation Models — облачный сервис, плата за который взимается в соответствии с тарифами.

## Установка и настройка

### Подготовка

1. Зарегистрируйтесь в [Cloud.ru](https://console.cloud.ru/registration/?zoneclick=github&retain_url=https://github.com/black-roland/homeassistant-cloud-ru-ai);
2. Получите [идентификатор проекта](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__project-id);
3. Зарегистрируйте [ключ API](https://cloud.ru/docs/console_api/ug/topics/guides__static-api-keys.html) с ролью `ml_inference_ai_marketplace`;
4. Сохраните полученные данные.

### Установка

1. [Скачайте интеграцию](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-cloud-ru-ai&category=integration) через HACS;
2. Перезапустите Home Assistant;
3. Перейдите в **Настройки → Устройства и службы → Добавить интеграцию** или используйте [кнопку настройки](https://my.home-assistant.io/redirect/config_flow_start/?domain=cloud_ru_ai);
4. Введите **иИдентификатор проекта** и **ключ API**, полученные в личном кабинете Cloud.ru.

## Примеры использования

Примеры использования можно найти в [моем блоге](https://mansmarthome.info/tags/ai/) — все статьи про YandexGPT актуальны и для этой интеграции.

TK: Скриншоты.

## Поддержка автора

Если интеграция оказалась полезной, вы можете [угостить автора чашечкой кофе](https://mansmarthome.info/donate/#donationalerts). Ваша благодарность ценится!

#### Благодарности

Огромное спасибо всем, кто поддерживает этот проект:

TK: Донат Владимира.

## Уведомление

Данная интеграция является неофициальной и не связана с Cloud.ru. Cloud.ru Foundation Models — это сервис, предоставляемый Cloud.ru.

Данная интеграция не является официальным продуктом Cloud.ru и не поддерживается Cloud.ru.
