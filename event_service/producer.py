import argparse
from typing import Any, Dict

from rabbitmq_client import publish_event


def event_payload(event_type: str, args: argparse.Namespace) -> Dict[str, Any]:
    if event_type == "user.created":
        return {
            "user_id": args.user_id,
            "login": args.login,
            "full_name": args.full_name,
        }

    if event_type == "driver.registered":
        return {
            "driver_id": args.driver_id,
            "user_id": args.user_id,
            "car_model": args.car_model,
            "car_number": args.car_number,
        }

    if event_type == "ride.created":
        return {
            "ride_id": args.ride_id,
            "user_id": args.user_id,
            "from_address": args.from_address,
            "to_address": args.to_address,
            "status": "active",
        }

    if event_type == "ride.accepted":
        return {
            "ride_id": args.ride_id,
            "driver_id": args.driver_id,
            "status": "accepted",
        }

    if event_type == "ride.completed":
        return {
            "ride_id": args.ride_id,
            "driver_id": args.driver_id,
            "user_id": args.user_id,
            "status": "completed",
            "price": args.price,
        }

    raise ValueError(f"Unsupported event type: {event_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish taxi domain event to RabbitMQ")

    parser.add_argument("event_type")

    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--driver-id", type=int, default=1)
    parser.add_argument("--ride-id", type=int, default=1)

    parser.add_argument("--login", default="ivan")
    parser.add_argument("--full-name", default="Ivan Petrov")

    parser.add_argument("--car-model", default="Skoda Octavia")
    parser.add_argument("--car-number", default="A123BC")

    parser.add_argument("--from-address", default="Airport")
    parser.add_argument("--to-address", default="City center")

    parser.add_argument("--price", type=float, default=750.0)

    args = parser.parse_args()

    payload = event_payload(args.event_type, args)
    publish_event(args.event_type, payload)


if __name__ == "__main__":
    main()
