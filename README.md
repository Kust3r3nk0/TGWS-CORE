# TGWS-CORE

**TGWS-CORE** — планируемое общее сетевое ядро для мобильных портов [TG WS Proxy от Flowseal](https://github.com/Flowseal/tg-ws-proxy).

> **Статус:** начальное проектирование. Реализация, тесты, артефакты и стабильный API пока отсутствуют.

## Назначение

Ядро используется мобильными приложениями [TGWS-CLODEX](https://github.com/Kust3r3nk0/TGWS-CLODEX), предназначенными для **Android 16+** и **iOS**. Ядро не должно зависеть от Android UI, SwiftUI или конкретных механизмов жизненного цикла ОС.

## Границы ядра (план)

- Локальный MTProto-прокси и управление его состоянием.
- Совместимое с оригинальным проектом поведение протокола, проверяемое тестами.
- Сетевые транспорты WebSocket/TLS, а также исследование fallback-сценариев.
- Управление соединениями: таймауты, повторные подключения, ограничения буферов и обратное давление (backpressure).
- Структурированные события диагностики без раскрытия секретов и пользовательского содержимого.
- Версионированный API для платформенных адаптеров Android и iOS.

## Вне ядра

- Android/iOS UI, разрешения ОС, foreground/background lifecycle.
- Политики распространения и обновления приложений.
- Системные сетевые расширения или службы, зависящие от платформы.

Эти компоненты находятся в [TGWS-CLODEX](https://github.com/Kust3r3nk0/TGWS-CLODEX).

## Архитектурные принципы

1. **Переносимость:** один код сетевой логики, отдельные платформенные обёртки.
2. **Безопасность:** локальный listener по умолчанию, корректная TLS-проверка, отсутствие секретов в логах.
3. **Надёжность:** конечные таймауты, контролируемые лимиты ресурсов, корректная остановка.
4. **Наблюдаемость:** воспроизводимые сетевые сценарии и стабильная схема диагностических событий.
5. **Тестируемость:** протокольные unit-тесты, интеграционные проверки и тесты отказов.
6. **Совместимость:** контроль поведения относительно upstream, без заявления об уже достигнутом паритете.

**Предварительный кандидат реализации:** Rust. Окончательный выбор языка, ABI и инструментов сборки принимается после технического прототипирования на обеих ОС.

## Критерии первого рабочего прототипа

- Запуск и остановка локального прокси через минимальный API.
- Подтверждённое подключение Telegram на Android **и** iOS.
- Обработка сетевого переключения и отсутствия соединения.
- Повторяемые тесты протокола и безопасная диагностика.
- Документированные ограничения, результаты тестов и известных проблем.

## Первоисточник и лицензирование

Референс: [Flowseal/tg-ws-proxy](https://github.com/Flowseal/tg-ws-proxy) (MIT License). TGWS-CORE — отдельная разработка, не официальный компонент Flowseal. Если будет использован исходный код upstream, необходимо сохранить требуемые уведомления и условия лицензий. Лицензия нового репозитория пока не определена.

---
*Этот README описывает целевую архитектуру; работающий прокси ещё не реализован.*

## Документация проекта

- [Техническое задание TGWS-CORE](./docs/TECHNICAL_SPECIFICATION.md)
- [Контракт интеграции ядра с Android/iOS](./docs/INTEGRATION_CONTRACT.md)
- [Техническое задание мобильных приложений TGWS-CLODEX](https://github.com/Kust3r3nk0/TGWS-CLODEX/blob/main/docs/TECHNICAL_SPECIFICATION.md)


## Architecture / security research (proposed)

- [Architecture and design decisions](docs/ARCHITECTURE.md) (complements the formal [Technical Specification](docs/TECHNICAL_SPECIFICATION.md) and [Integration Contract](docs/INTEGRATION_CONTRACT.md))
- [Network flows](docs/NETWORK_INTERACTIONS.md) · [Threat model](docs/SECURITY_THREAT_MODEL.md) · [Experiment plan](docs/EXPERIMENTS.md)
- [Test matrix](docs/TEST_MATRIX.md) · [Security policy](SECURITY.md)

**SPEC_ONLY:** There is **no runnable** core. The command `python3 -m unittest discover -s tests -p 'test_*.py' -v` **only validates** the design fixtures; it does not test MTProto traffic, TLS, Android, iOS or deployed relays.
