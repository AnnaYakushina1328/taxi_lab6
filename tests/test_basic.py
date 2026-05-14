# Start via `make test-debug` or `make test-release`


import json
import uuid


async def _create_user_and_get_token(service_client):
    login = f"cache_test_{uuid.uuid4().hex[:8]}"
    password = "pass123"
    full_name = "Cache Test User"

    create_response = await service_client.post(
        "/users",
        json={
            "login": login,
            "password": password,
            "full_name": full_name,
        },
    )

    assert create_response.status == 201

    login_response = await service_client.post(
        "/auth/login",
        json={
            "login": login,
            "password": password,
        },
    )

    assert login_response.status == 200

    body = json.loads(login_response.text)
    assert "token" in body
    assert body["token"]

    return body["token"]


async def test_ping(service_client):
    response = await service_client.get("/ping")
    assert response.status == 200


async def test_users_cache_header(service_client):
    token = await _create_user_and_get_token(service_client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = await service_client.get(
        "/users",
        params={"name_mask": "Cache"},
        headers=headers,
    )

    assert first_response.status == 200
    assert first_response.headers["X-Cache"] == "MISS"

    second_response = await service_client.get(
        "/users",
        params={"name_mask": "Cache"},
        headers=headers,
    )

    assert second_response.status == 200
    assert second_response.headers["X-Cache"] == "HIT"


async def test_active_rides_cache_and_rate_limit_headers(service_client):
    token = await _create_user_and_get_token(service_client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = await service_client.get(
        "/rides",
        params={"status": "active"},
        headers=headers,
    )

    assert first_response.status == 200
    assert first_response.headers["X-Cache"] == "MISS"
    assert first_response.headers["X-RateLimit-Limit"] == "100"
    assert "X-RateLimit-Remaining" in first_response.headers
    assert "X-RateLimit-Reset" in first_response.headers

    second_response = await service_client.get(
        "/rides",
        params={"status": "active"},
        headers=headers,
    )

    assert second_response.status == 200
    assert second_response.headers["X-Cache"] == "HIT"
    assert second_response.headers["X-RateLimit-Limit"] == "100"
    assert "X-RateLimit-Remaining" in second_response.headers
    assert "X-RateLimit-Reset" in second_response.headers


async def test_active_rides_rate_limit_429(service_client):
    token = await _create_user_and_get_token(service_client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    last_response = None

    for _ in range(105):
        last_response = await service_client.get(
            "/rides",
            params={"status": "active"},
            headers=headers,
        )

        if last_response.status == 429:
            break

    assert last_response is not None
    assert last_response.status == 429

    assert last_response.headers["X-RateLimit-Limit"] == "100"
    assert last_response.headers["X-RateLimit-Remaining"] == "0"
    assert "X-RateLimit-Reset" in last_response.headers
    assert "Retry-After" in last_response.headers
