# Лабораторная работа 6. Event-Driven архитектура в сервисе такси

Вариант 16: система заказа такси.

## Что делает проект

Проект сделан на основе предыдущей лабораторной работы с сервисом такси. В системе остаются основные сущности:

- пользователь;
- водитель;
- поездка.

Базовый сценарий такой: пассажир создаёт заказ, водитель принимает его, после выполнения поездка завершается и попадает в историю.

В шестой лабораторной добавлена событийная часть. Теперь важные изменения в системе можно передавать как события через RabbitMQ.

## Какие события используются

В проекте описаны события:

- `user.created`;
- `driver.registered`;
- `ride.created`;
- `ride.accepted`;
- `ride.completed`.

Эти события соответствуют основным действиям в системе заказа такси.

## Что добавлено в шестой лабораторной

Добавлены файлы:

- `event_driven_design.md` — описание событийной архитектуры;
- `event_catalog.md` — каталог событий;
- `event_service/producer.py` — отправка событий в RabbitMQ;
- `event_service/consumer.py` — обработка событий поездок;
- `event_service/test_events.py` — тестовый сценарий;
- `event_service/rabbitmq_client.py` — подключение к RabbitMQ и создание exchange/queues;
- `event_service/Dockerfile` — сборка сервиса событий;
- `docker-compose.yaml` — запуск API, баз данных, RabbitMQ и consumer.

## RabbitMQ

Используется RabbitMQ с management UI.

Exchange:

```text
taxi.events
```

Тип exchange:

```text
topic
```

Routing key совпадает с названием события:

```text
ride.created
ride.accepted
ride.completed
```

## Очереди

| Очередь | Что получает |
|---|---|
| taxi.notifications | события для возможных уведомлений |
| taxi.ride_read_model | события поездок для read-модели |
| taxi.audit | все события |

В коде consumer слушает очередь `taxi.audit`, поэтому в логах видны все события. При этом read-модель обновляется только по событиям поездок.

## Запуск

Собрать и запустить контейнеры:

```bash
docker compose up --build -d
```

Проверить состояние:

```bash
docker compose ps
```

RabbitMQ UI:

```text
http://localhost:15672
```

Логин:

```text
taxi
```

Пароль:

```text
taxi123
```

## Проверка событий

Отправить тестовую цепочку событий:

```bash
docker compose run --rm event-producer
```

Посмотреть логи consumer:

```bash
docker compose logs event-consumer
```

Проверить read-модель:

```bash
docker compose exec event-consumer cat /data/read_model.json
```

После тестового сценария поездка должна оказаться в `completed_rides`.

## Отправка одного события вручную

Создать событие новой поездки:

```bash
docker compose run --rm event-producer python producer.py ride.created --ride-id 200 --user-id 1 --from-address "MAI" --to-address "Airport"
```

Принять поездку:

```bash
docker compose run --rm event-producer python producer.py ride.accepted --ride-id 200 --driver-id 10
```

Завершить поездку:

```bash
docker compose run --rm event-producer python producer.py ride.completed --ride-id 200 --driver-id 10 --user-id 1 --price 900
```

Проверить read-модель:

```bash
docker compose exec event-consumer cat /data/read_model.json
```

## CQRS

CQRS применён в упрощённом виде.

Команды меняют состояние:

- создание пользователя;
- регистрация водителя;
- создание заказа;
- принятие заказа;
- завершение поездки.

Запросы читают подготовленное состояние:

- активные поездки;
- принятые поездки;
- завершённые поездки.

Consumer обновляет отдельную read-модель на основе событий. В этой лабораторной она хранится в JSON-файле, чтобы результат было легко проверить. В настоящем сервисе такую модель можно было бы хранить в MongoDB, Redis или отдельной таблице.

## Гарантии доставки

Используется гарантия `at-least-once`.

Для этого в RabbitMQ используются durable queues, persistent messages и ручное подтверждение обработки. Если consumer не смог обработать сообщение, оно возвращается обратно в очередь.

## Остановка

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volumes:

```bash
docker compose down -v
```

## Документация

Основные документы по шестой лабораторной:

- `event_driven_design.md`;
- `event_catalog.md`.
