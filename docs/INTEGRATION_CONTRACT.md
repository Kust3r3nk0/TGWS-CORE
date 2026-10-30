# Контракт интеграции TGWS-CORE ↔ TGWS-CLODEX

**Идентификатор:** CONTRACT-CORE-MOBILE-001  
**Версия документа:** 0.1-draft  
**Дата:** 2026-10-30  
**Владелец контракта:** TGWS-CORE.  
**Потребители:** нативные Android и iOS приложения TGWS-CLODEX.

> Это **логический контракт проектирования**, а не декларация об уже существующей бинарной библиотеке. Синтаксис окончательного ABI и формат bindings утверждаются отдельным ADR после испытаний на Android/iOS.

## 1. Принципы

- Одна семантика ядра для Android и iOS.
- Никаких объектов Rust/Python/Swift/Kotlin напрямую через границу ABI.
- Одинаковые коды ошибок и переходы состояний.
- Долгие сетевые операции не блокируют UI или поток callback.
- На ошибке ресурс освобождается; после stop он не используется.
- Секреты передаются ядру только в памяти и не появляются в событиях, логах, экспортируемых отчётах.
- UI не выводит «Telegram подключён» на основании одного только успешного bind порта.

## 2. Обязательные операции (логический API)

| ID | Операция | Вход / выход | Обязательная семантика |
| --- | --- | --- | --- |
| API-01 | get_capabilities | abi_version, core_version, feature_flags | Без запуска сети; несовместимые major версии обнаруживаются до create |
| API-02 | validate_config | Config -> ValidationResult | Чистая проверка; нет side effects и сохранения секрета |
| API-03 | create | validated Config -> opaque CoreHandle | Создаёт состояние CREATED; listener ещё не открыт |
| API-04 | start | CoreHandle -> async result | Success только после подтверждённого bind и запуска accept loop |
| API-05 | stop | CoreHandle -> async result | При повторном stop остаётся безопасным; закрывает все ресурсы |
| API-06 | get_state | CoreHandle -> CoreSnapshot | Консистентный снимок состояния listener и счётчиков |
| API-07 | subscribe_events | CoreHandle, sink -> Subscription | События имеют версию схемы; backpressure и частота ограничены |
| API-08 | unsubscribe_events | Subscription -> Result | После подтверждения отписки callback больше не вызывается |
| API-09 | get_diagnostics | CoreHandle -> SafeReport | Только агрегированные/redacted данные |
| API-10 | destroy | CoreHandle -> Result | После завершения stop освобождает handle; недопустим двойной free |

Изменение конфигурации работающего ядра по умолчанию производится через валидированный **stop -> create/start** и атомарное обновление модели UI. Hot reload допустим только после отдельного ADR.

## 3. Предлагаемая конфигурационная схема v1

~~~json
{
  "schema_version": 1,
  "listener": {
    "host": "127.0.0.1",
    "port": 1443
  },
  "mtproto": {
    "secret_hex": "<runtime-secret-from-platform-secure-storage>"
  },
  "transport": {
    "primary": "websocket_tls",
    "fallback_policy": "disabled"
  },
  "limits": {
    "max_sessions": 16,
    "connect_timeout_ms": 10000
  }
}
~~~

- Значения выше — **первичная схема для обсуждения**, не значения, уже утверждённые бенчмарком.
- Поле secret_hex присутствует только во временном объекте, созданном адаптером из Keychain/Keystore; конфигурация с plaintext-secret **не записывается** на диск.
- host по умолчанию строго loopback; любые external bind endpoints запрещены без отдельного security ADR.
- Неизвестные schema_version/transport/feature_flag возвращают E_UNSUPPORTED_CONFIG, не игнорируются молча.
- Диапазон порта — 1..65535; 0 для auto-select может быть добавлен только явным решением UI/ABI.
- Все размеры, timeouts и списки ограничены и проходят явную валидацию.
- При включении любых fallback будущая схема обязана раскрывать их пользователю и передавать структурированный transport-change event.

## 4. Состояния и события

### ListenerState

CREATED / STARTING / RUNNING / STOPPING / STOPPED / ERROR.

**Принцип:** RUNNING означает работоспособность локального listener, а не проверенное подключение Telegram к DC. Состояние upstream отображается **отдельным полем**.

### События

| Event | Минимальные поля |
| --- | --- |
| LISTENER_STATE_CHANGED | state, timestamp, sequence |
| SESSION_OPENED / SESSION_CLOSED | session_id (случайный локальный идентификатор), timestamp, aggregate counters |
| UPSTREAM_CONNECTING / UPSTREAM_READY | transport_id, dc_code (при необходимости), timestamp |
| TRANSPORT_FAILED / TRANSPORT_SWITCHED | previous/next transport, stable error_code, retry_hint |
| NETWORK_UNAVAILABLE | timestamp, retry_hint |
| CORE_ERROR | stable error_code, severity, safe_message_key |
| STATS_SNAPSHOT | active_sessions, sent_bytes, received_bytes, error_counts |

Запрещены: raw MTProto secret, ключи/IV, payload пакетов, тексты сообщений, username, user_id Telegram, содержимое deeplink, IP клиентов и query-строки URL.

**Порядок:** для конкретного CoreHandle события несут монотонный sequence number. Callback может быть вызван не на UI-потоке. При переполнении очереди допускается coalescing счётчиков, но не потеря терминальных событий STOPPED/ERROR.

## 5. Коды ошибок v1 (предлагаемый набор)

| Код | Причина | Возможное действие мобильного UI |
| --- | --- | --- |
| E_INVALID_CONFIG | Неправильная конфигурация | Показать нарушенное поле |
| E_ABI_MISMATCH | Несовместимая версия библиотеки | Заблокировать запуск и показать версию |
| E_ADDR_IN_USE | Порт занят | Предложить другой порт |
| E_BIND_DENIED | ОС запретила открытие сокета | Показать системное ограничение |
| E_BAD_SECRET | Секрет не принят или неверен | Предложить безопасную ротацию |
| E_UNSUPPORTED_CONFIG | Неизвестный transport или поле | Предложить обновить версию/настройки |
| E_NETWORK_OFFLINE | Нет uplink | Повторить после восстановления сети |
| E_DNS_FAILED | Ошибка DNS | Показать сетевую ошибку |
| E_TLS_INVALID_PEER | Неверный TLS сертификат/имя | Не предлагать «отключить проверку» |
| E_WS_HANDSHAKE | Ошибка согласования WebSocket | Показать transport status |
| E_UPSTREAM_UNREACHABLE | Telegram DC недоступен | Предложить проверить сеть/режим |
| E_TIMEOUT | Истёк таймаут | Безопасный retry по policy |
| E_RESOURCE_LIMIT | Достигнут лимит памяти/сессий | Ограничить новые сессии |
| E_PLATFORM_RESTRICTED | Ограничение iOS/Android adapter | Показать точную причину, не утверждать RUNNING |
| E_INTERNAL | Контролируемая внутренняя ошибка | Диагностика с redaction |

Коды являются частью стабильного контракта; не использовать локализованный текст как идентификатор ошибки. Секреты никогда не включать в описания исключений.

## 6. Ownership, threading и безопасность FFI

- Окончательное API на C ABI, UniFFI или другом binding-tool выбрать по ADR.
- CoreHandle — opaque и привязан к конкретной версии runtime; оба платформенных адаптера имеют эквивалентную семантику.
- Кросс-языковые строки/буферы передаются с явно документированными length, encoding и функцией освобождения.
- Нельзя хранить заемные указатели, если lifetime вызывающей стороны закончился.
- Callback не удерживается и не вызывается после подтверждённого unsubscribe/destroy.
- stop/destroy должны безопасно обрабатывать гонки с network callback, shutdown и error propagation.
- Panic/exception ни при каких условиях не пересекает FFI boundary и не становится неопределённым поведением.
- UI обновляется на главном потоке **мобильным адаптером**, не самим ядром.
- Все API имеют явные preconditions, postconditions и тесты на null/invalid handles.
- Версия core и capabilities доступны до создания CoreHandle.

## 7. Версии и feature negotiation

- Публичная схема: schema_version (начальная 1).
- Версия ABI: major/minor, начиная с 0.x в прототипе.
- Версия реализации: semantic version TGWS-CORE; приложения фиксируют точную зависимость.
- Неподдерживаемая **major** ABI или schema — жёсткий отказ до запуска.
- Необязательные функции: capability flags для cf_worker, cfproxy, direct_tcp, h2, fake_tls, metrics и др. Их присутствие не означает включённость/работоспособность.
- Функцию можно показывать в UI только если capability задокументирована и реально прошла platform test.
- В artifact metadata хранятся версия ядра, исходный commit и checksum.

## 8. Контрактные тесты для обеих платформ

| Тест | Ожидаемый результат |
| --- | --- |
| api_version_normal / mismatch | Корректный набор версий / E_ABI_MISMATCH |
| validate_config_bad_port / secret | Соответствующая ошибка без открытия сокета |
| start_and_stop | RUNNING только после bind, STOPPED после полного shutdown |
| duplicate_start / stop / destroy | Нет crash, double-free, зависания |
| listener_bind_conflict | E_ADDR_IN_USE, состояние не выдаёт RUNNING |
| callback_unsubscribe_race | Нет событий после подтверждённой отписки |
| callback_queue_overflow | Финальные события доставлены; счётчики ограничены |
| no_secret_in_events | 0 утечек подготовленной test secret в event stream |
| network_offline_recovery | Структурированная ошибка, восстановление по policy |
| unsupported_transport | Явный E_UNSUPPORTED_CONFIG |

### Приёмка интерфейса

Контракт считается готовым, когда **один и тот же тестовый набор** семантических сценариев успешно выполнен через Android-адаптер и iOS-адаптер; результаты привязаны к версионным артефактам. Это не заменяет платформенный feasibility gate фоновой работы iOS из ТЗ TGWS-CLODEX.

## 9. Процедура изменения

Изменение структуры Config, состояний, ошибок, callback semantics, распределения памяти или threading требует:

1. ADR с обоснованием, совместимостью и угрозами.
2. Повышения соответствующей версии контрактов.
3. Обновления обоих ТЗ.
4. Обновления тестовых адаптеров Android и iOS.
5. Release notes с breaking changes и миграционными требованиями.

**Связанные документы:** [TGWS-CORE — ТЗ](./TECHNICAL_SPECIFICATION.md), [TGWS-CLODEX — ТЗ](https://github.com/Kust3r3nk0/TGWS-CLODEX/blob/main/docs/TECHNICAL_SPECIFICATION.md).