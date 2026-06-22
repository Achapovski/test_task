# Payment Processing Service

Backend-сервис обработки платежей, реализованный на **FastAPI** и **RabbitMQ**
с использованием **Outbox Pattern**.

---

# Стек технологий

* FastAPI
* SQLAlchemy
* PostgreSQL
* RabbitMQ
* FastStream
* Dishka
* Docker

---

# Возможности

* Создание платежа
* Получение информации о платеже
* Outbox Pattern для гарантированной доставки событий
* Асинхронная обработка платежей через RabbitMQ
* Эмуляция внешнего платежного шлюза
* Отправка webhook после успешной обработки
* Retry-механизм при ошибках доставки webhook
* Dead Letter Queue (DLQ) для необработанных сообщений
* Unit и integration тесты

---

Структура проекта:

```
src/
├── app/
│   ├── dto/
│   ├── interfaces/
│   ├── use_cases/
│   ├── entrypoints/
│   └── exceptions/
│
├── domains/
│   └── payments/
├── infra/
│   ├── adapters/
│   ├── messaging/
│   ├── outbox/
│   └── entrypoints/
├── core/
│
├──containters.py
├──bootstrap.py
└── main.py
```

## Запуск

Независимо от запуска необходимо создать `config.yml` и `.env` примеры структур которых описаны в соответствующих
`.example` файлах

## Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска будут доступны:

* FastAPI — http://localhost:8080
* Swagger — http://localhost:8080/docs
* RabbitMQ Management — http://localhost:15672

---

# Миграции

Создание миграции:

```bash
alembic revision --autogenerate -m "init"
```

Применение миграций:

```bash
alembic upgrade head
```

---

# REST API

Бизнес логика проекта вынесена в сценарии использования `/app/use_cases`, которые агрегируют управление сущностями и
сессией БД.

## Создание платежа

### POST /api/v1/payments

Headers:

```http
Idempotency-Key: 7e4a99b8-bb7d-4af6-9dbf-8f62d463bafb
X-API-Key: SecretKey
```

Body:

```json
{
  "amount": 100.00,
  "currency": "USD",
  "description": "Order #123",
  "metadata": {
    "user_id": 1
  },
  "webhook_url": "https://example.com/webhook"
}
```

Response:

```json
{
  "id": "5bfc4131-5a58-48d0-a0d3-c2bb16b16dd8",
  "amount": 100.00,
  "currency": "USD",
  "status": "PENDING"
}
```

---

## Получение платежа

### GET /api/v1/payments/{payment_id}

Headers:

```http
X-API-Key: SecretKey
```

Response:

```json
{
  "id": "a69b3d0e-365f-475e-a729-3f376dfe4efb",
  "idempotency_key": "3fa85f64-5717-4562-b3fc-2c963f66afa2",
  "amount": "1.00",
  "currency": "USD",
  "metadata": null,
  "description": "string",
  "status": "SUCCESS",
  "webhook_url": "https://google.com",
  "created_at": "2026-06-19T18:15:00.577431Z",
  "processed_at": null
}
```

---

# Outbox Pattern

При создании платежа событие сохраняется в таблицу `outbox`.
Отдельный publisher публикует события в RabbitMQ только после успешной фиксации транзакции.
---

# Обработка платежей

Consumer получает событие:

```text
payments.new
```

и имитирует внешний платежный шлюз.

После обработки статус платежа изменяется на:

* SUCCESS
* FAILED

---

# Webhook

При успешной обработке платежа отправляется HTTP webhook:

```json
{
  "payment_id": "<uuid>",
  "status": "SUCCESS"
}
```

---

# Retry Policy

При ошибке отправки webhook используется экспоненциальный retry.
После исчерпания лимита сообщение отправляется в DLQ.

---

# Тестирование

Запуск всех тестов:

```bash
pytest
```

Запуск unit-тестов:

```bash
pytest tests/units
```

Запуск integration-тестов:

```bash
pytest tests/integrations
```
