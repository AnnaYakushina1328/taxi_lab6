# Документная модель MongoDB для сервиса такси

Этот файл остался как часть расширения проекта под MongoDB. Основная пятая лабораторная работа описана в `README.md` и `performance_design.md`, а здесь кратко зафиксирована документная модель, которая использовалась раньше.

## Сущности

Для варианта 16 используются три основные коллекции:

- `users`;
- `drivers`;
- `rides`.

Такой вариант совпадает с предметной областью сервиса такси: отдельно хранятся пассажиры, водители и поездки.

## Коллекция users

Документ пользователя хранит данные аккаунта и небольшой вложенный профиль.

Пример:

```json
{
  "_id": { "$oid": "671111111111111111111111" },
  "login": "ivan.petrov",
  "password": "hashed_password_value",
  "first_name": "Ivan",
  "last_name": "Petrov",
  "created_at": { "$date": "2026-04-18T10:00:00Z" },
  "status": "active",
  "profile": {
    "email": "ivan.petrov@example.com",
    "phone": "+79990000001"
  }
}
```

`profile` хранится внутри пользователя, потому что это небольшие данные, которые отдельно от пользователя не используются.

## Коллекция drivers

Документ водителя хранит информацию о водителе, машине и водительском профиле.

Пример:

```json
{
  "_id": { "$oid": "672222222222222222222222" },
  "login": "driver.alex",
  "first_name": "Alexey",
  "last_name": "Sidorov",
  "status": "available",
  "registered_at": { "$date": "2026-04-18T10:15:00Z" },
  "car": {
    "brand": "Kia",
    "model": "Rio",
    "plate_number": "A123BC777",
    "color": "white"
  },
  "profile": {
    "phone": "+79990000021",
    "license_number": "77AB123456"
  }
}
```

`car` и `profile` сделаны embedded document, потому что они принадлежат конкретному водителю и обычно читаются вместе с ним.

## Коллекция rides

Поездка хранится отдельным документом, потому что у неё свой жизненный цикл: создание, принятие водителем и завершение.

Пример:

```json
{
  "_id": { "$oid": "673333333333333333333333" },
  "user_id": { "$oid": "671111111111111111111111" },
  "driver_id": { "$oid": "672222222222222222222222" },
  "status": "accepted",
  "created_at": { "$date": "2026-04-18T11:00:00Z" },
  "accepted_at": { "$date": "2026-04-18T11:03:00Z" },
  "completed_at": null,
  "route": {
    "pickup_address": "Moscow, Leningradsky prospekt, 1",
    "dropoff_address": "Moscow, Tverskaya, 10"
  },
  "fare": {
    "amount": 650,
    "currency": "RUB"
  },
  "events": [
    {
      "type": "created",
      "at": { "$date": "2026-04-18T11:00:00Z" }
    }
  ]
}
```

## Embedded и references

Внутри документов оставлены небольшие вложенные объекты:

- `users.profile`;
- `drivers.car`;
- `drivers.profile`;
- `rides.route`;
- `rides.fare`;
- `rides.events`.

References используются для связей:

- `rides.user_id` -> `users._id`;
- `rides.driver_id` -> `drivers._id`.

Я не стала вкладывать все поездки внутрь пользователя или водителя, потому что история поездок может расти без ограничений. Отдельная коллекция `rides` проще для поиска активных заказов и истории поездок.
