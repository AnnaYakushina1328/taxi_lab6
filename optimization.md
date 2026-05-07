# Оптимизация SQL-запросов

Вариант 16: система заказа такси.

Этот файл относится к части проекта с PostgreSQL. Здесь кратко описаны индексы и типовые запросы, которые используются в сервисе.

## Основные таблицы

В базе используются три таблицы:

- `users`;
- `drivers`;
- `rides`.

Они покрывают основные операции сервиса: регистрацию пользователей, регистрацию водителей, создание и обработку поездок.

## Индексы

### users

Для пользователей важны два сценария:

- поиск по логину;
- поиск по части имени.

Логин уникален, поэтому PostgreSQL автоматически создаёт индекс для ограничения `UNIQUE`.

Для поиска по имени используется trigram-индекс:

```sql
CREATE INDEX idx_users_full_name_trgm
ON users USING GIN (lower(full_name) gin_trgm_ops);
```

Он помогает запросам вида:

```sql
WHERE lower(full_name) LIKE '%' || lower($1) || '%'
```

### drivers

Для водителей используются индексы:

```sql
CREATE INDEX idx_drivers_status ON drivers(status);
CREATE INDEX idx_drivers_user_id ON drivers(user_id);
```

`idx_drivers_status` нужен для выборки водителей по статусу, а `idx_drivers_user_id` — для поиска водителя по пользователю.

### rides

Для поездок используются индексы:

```sql
CREATE INDEX idx_rides_passenger_id ON rides(passenger_id);
CREATE INDEX idx_rides_driver_id ON rides(driver_id);
CREATE INDEX idx_rides_status ON rides(status);
CREATE INDEX idx_rides_passenger_status ON rides(passenger_id, status);
CREATE INDEX idx_rides_created_at ON rides(created_at DESC);
```

Они нужны для:

- получения истории поездок пользователя;
- получения поездок конкретного водителя;
- выборки активных поездок;
- сортировки поездок по времени создания.

## Примеры запросов

### Поиск пользователя по логину

```sql
SELECT id, login, full_name
FROM users
WHERE login = 'test.user';
```

Для такого запроса используется индекс по уникальному полю `login`.

### Получение активных поездок

```sql
SELECT id, passenger_id, driver_id, pickup_address, destination_address, status
FROM rides
WHERE status IN ('searching', 'accepted')
ORDER BY id;
```

На маленьком тестовом наборе PostgreSQL может выбрать `Seq Scan`, потому что строк мало. При росте таблицы индекс по `status` становится полезнее.

### Получение истории поездок пользователя

```sql
SELECT id, passenger_id, driver_id, pickup_address, destination_address, status
FROM rides
WHERE passenger_id = 11
ORDER BY created_at DESC, id DESC;
```

Для этого запроса полезны индексы по `passenger_id` и `created_at`.

## Вывод

Индексы выбраны под основные операции API. На маленьких тестовых данных разница может быть почти незаметна, но при росте количества пользователей, водителей и поездок они уменьшают количество полных сканирований таблиц.
