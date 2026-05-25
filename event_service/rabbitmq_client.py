import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

import pika


EXCHANGE_NAME = "taxi.events"
EXCHANGE_TYPE = "topic"

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "taxi")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "taxi123")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=30,
    )

    last_error = None

    for _ in range(20):
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError as error:
            last_error = error
            time.sleep(2)

    raise RuntimeError(f"RabbitMQ is not available: {last_error}")


def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True,
    )

    queues = {
        "taxi.notifications": [
            "user.created",
            "driver.registered",
            "ride.created",
            "ride.accepted",
            "ride.completed",
        ],
        "taxi.ride_read_model": [
            "ride.created",
            "ride.accepted",
            "ride.completed",
        ],
        "taxi.audit": [
            "#",
        ],
    }

    for queue_name, routing_keys in queues.items():
        channel.queue_declare(queue=queue_name, durable=True)

        for routing_key in routing_keys:
            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue_name,
                routing_key=routing_key,
            )


def make_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "event_id": f"{event_type}-{int(time.time() * 1000)}",
        "event_type": event_type,
        "occurred_at": utc_now(),
        "source": "taxi-service",
        "payload": payload,
    }


def publish_event(event_type: str, payload: Dict[str, Any]) -> None:
    event = make_event(event_type, payload)

    connection = get_connection()
    channel = connection.channel()

    declare_topology(channel)

    body = json.dumps(event, ensure_ascii=False).encode("utf-8")

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=event_type,
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=pika.DeliveryMode.Persistent,
        ),
    )

    print(f"published {event_type}: {json.dumps(event, ensure_ascii=False)}")

    connection.close()
