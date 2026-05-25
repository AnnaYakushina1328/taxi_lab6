import json
import os
from pathlib import Path
from typing import Any, Dict

from rabbitmq_client import get_connection, declare_topology


READ_MODEL_PATH = Path(os.getenv("READ_MODEL_PATH", "/data/read_model.json"))


def load_read_model() -> Dict[str, Any]:
    if not READ_MODEL_PATH.exists():
        return {
            "active_rides": {},
            "accepted_rides": {},
            "completed_rides": {},
            "last_events": [],
        }

    with READ_MODEL_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_read_model(model: Dict[str, Any]) -> None:
    READ_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    with READ_MODEL_PATH.open("w", encoding="utf-8") as file:
        json.dump(model, file, ensure_ascii=False, indent=2)


def update_read_model(event: Dict[str, Any]) -> None:
    model = load_read_model()

    event_type = event["event_type"]
    payload = event["payload"]

    if event_type == "ride.created":
        ride_id = str(payload["ride_id"])
        model["active_rides"][ride_id] = payload

    elif event_type == "ride.accepted":
        ride_id = str(payload["ride_id"])
        ride = model["active_rides"].pop(ride_id, {})
        ride.update(payload)
        model["accepted_rides"][ride_id] = ride

    elif event_type == "ride.completed":
        ride_id = str(payload["ride_id"])
        ride = model["accepted_rides"].pop(ride_id, {})
        ride.update(payload)
        model["completed_rides"][ride_id] = ride

    model["last_events"].append(
        {
            "event_type": event_type,
            "event_id": event["event_id"],
            "occurred_at": event["occurred_at"],
        }
    )

    model["last_events"] = model["last_events"][-20:]

    save_read_model(model)


def handle_message(channel, method, properties, body) -> None:
    try:
        event = json.loads(body.decode("utf-8"))

        print(
            "received "
            f"{event['event_type']} "
            f"from {event.get('source', 'unknown')}: "
            f"{json.dumps(event['payload'], ensure_ascii=False)}",
            flush=True,
        )

        if event["event_type"].startswith("ride."):
            update_read_model(event)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        print(f"failed to process message: {error}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main() -> None:
    connection = get_connection()
    channel = connection.channel()

    declare_topology(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="taxi.audit",
        on_message_callback=handle_message,
    )

    print("event consumer started; audit queue logs all events, ride events update read model", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
