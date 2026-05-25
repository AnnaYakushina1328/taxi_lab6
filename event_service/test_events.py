from rabbitmq_client import publish_event


def main() -> None:
    publish_event(
        "user.created",
        {
            "user_id": 1,
            "login": "anna",
            "full_name": "Anna Yakushina",
        },
    )

    publish_event(
        "driver.registered",
        {
            "driver_id": 10,
            "user_id": 2,
            "car_model": "Kia Rio",
            "car_number": "B777AA",
        },
    )

    publish_event(
        "ride.created",
        {
            "ride_id": 100,
            "user_id": 1,
            "from_address": "MAI",
            "to_address": "Sokol metro station",
            "status": "active",
        },
    )

    publish_event(
        "ride.accepted",
        {
            "ride_id": 100,
            "driver_id": 10,
            "status": "accepted",
        },
    )

    publish_event(
        "ride.completed",
        {
            "ride_id": 100,
            "driver_id": 10,
            "user_id": 1,
            "status": "completed",
            "price": 420.0,
        },
    )


if __name__ == "__main__":
    main()
