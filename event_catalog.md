# Каталог событий системы заказа такси

## Общий формат события

Все события передаются через RabbitMQ в формате JSON.

```json
{
  "event_id": "unique-event-id",
  "event_type": "ride.created",
  "occurred_at": "2026-05-25T10:00:00+00:00",
  "source": "taxi-service",
  "payload": {}
}
```

| Поле | Описание |
|---|---|
| event_id | уникальный идентификатор события |
| event_type | тип события |
| occurred_at | время появления события |
| source | сервис, который опубликовал событие |
| payload | данные конкретного события |

Exchange:

```text
taxi.events
```

Тип exchange:

```text
topic
```

Гарантия доставки:

```text
at-least-once
```

---

## user.created

Событие появляется после создания пользователя.

### Payload

```json
{
  "user_id": 1,
  "login": "anna",
  "full_name": "Anna Yakushina"
}
```

### Producer

| Producer |
|---|
| taxi-service |

### Consumers

| Consumer | Зачем получает событие |
|---|---|
| Notification Service | может отправить приветственное уведомление |
| Audit Service | сохраняет факт создания пользователя |

### Routing

| Параметр | Значение |
|---|---|
| Routing key | user.created |
| Queue | taxi.notifications, taxi.audit |

### Гарантия доставки

`at-least-once`.

---

## driver.registered

Событие появляется после регистрации водителя.

### Payload

```json
{
  "driver_id": 10,
  "user_id": 2,
  "car_model": "Kia Rio",
  "car_number": "B777AA"
}
```

### Producer

| Producer |
|---|
| taxi-service |

### Consumers

| Consumer | Зачем получает событие |
|---|---|
| Notification Service | может уведомить водителя об успешной регистрации |
| Audit Service | сохраняет факт регистрации водителя |

### Routing

| Параметр | Значение |
|---|---|
| Routing key | driver.registered |
| Queue | taxi.notifications, taxi.audit |

### Гарантия доставки

`at-least-once`.

---

## ride.created

Событие появляется после создания заказа поездки.

### Payload

```json
{
  "ride_id": 100,
  "user_id": 1,
  "from_address": "MAI",
  "to_address": "Sokol metro station",
  "status": "active"
}
```

### Producer

| Producer |
|---|
| taxi-service |

### Consumers

| Consumer | Зачем получает событие |
|---|---|
| Ride Read Model Service | добавляет заказ в список активных поездок |
| Notification Service | может уведомить водителей о новом заказе |
| Audit Service | сохраняет историю изменения |

### Routing

| Параметр | Значение |
|---|---|
| Routing key | ride.created |
| Queue | taxi.ride_read_model, taxi.notifications, taxi.audit |

### Гарантия доставки

`at-least-once`.

### Изменение read-модели

Заказ добавляется в раздел:

```text
active_rides
```

---

## ride.accepted

Событие появляется после принятия заказа водителем.

### Payload

```json
{
  "ride_id": 100,
  "driver_id": 10,
  "status": "accepted"
}
```

### Producer

| Producer |
|---|
| taxi-service |

### Consumers

| Consumer | Зачем получает событие |
|---|---|
| Ride Read Model Service | переносит поездку из активных в принятые |
| Notification Service | может уведомить пассажира, что водитель найден |
| Audit Service | сохраняет изменение статуса |

### Routing

| Параметр | Значение |
|---|---|
| Routing key | ride.accepted |
| Queue | taxi.ride_read_model, taxi.notifications, taxi.audit |

### Гарантия доставки

`at-least-once`.

### Изменение read-модели

Заказ удаляется из:

```text
active_rides
```

и добавляется в:

```text
accepted_rides
```

---

## ride.completed

Событие появляется после завершения поездки.

### Payload

```json
{
  "ride_id": 100,
  "driver_id": 10,
  "user_id": 1,
  "status": "completed",
  "price": 420.0
}
```

### Producer

| Producer |
|---|
| taxi-service |

### Consumers

| Consumer | Зачем получает событие |
|---|---|
| Ride Read Model Service | переносит поездку в завершённые |
| Notification Service | может отправить итог поездки |
| Audit Service | сохраняет финальное состояние поездки |

### Routing

| Параметр | Значение |
|---|---|
| Routing key | ride.completed |
| Queue | taxi.ride_read_model, taxi.notifications, taxi.audit |

### Гарантия доставки

`at-least-once`.

### Изменение read-модели

Заказ удаляется из:

```text
accepted_rides
```

и добавляется в:

```text
completed_rides
```

---

## Итоговая таблица событий

| Событие | Producer | Основные consumers | Routing key |
|---|---|---|---|
| user.created | taxi-service | notifications, audit | user.created |
| driver.registered | taxi-service | notifications, audit | driver.registered |
| ride.created | taxi-service | ride_read_model, notifications, audit | ride.created |
| ride.accepted | taxi-service | ride_read_model, notifications, audit | ride.accepted |
| ride.completed | taxi-service | ride_read_model, notifications, audit | ride.completed |
