"""Auth endpoint tests."""

from typing import Any

from httpx import AsyncClient


async def _register(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "securepassword123",
) -> dict[str, Any]:
    """Helper to register a user and return the response JSON."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    return response.json()


async def test_register_success(client: AsyncClient) -> None:
    """Register returns 201 with tokens."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["error"] is None


async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Register with existing email returns 409."""
    await _register(client)
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword1"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_EMAIL"


async def test_register_weak_password(client: AsyncClient) -> None:
    """Register with password < 8 chars returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422


async def test_login_success(client: AsyncClient) -> None:
    """Login with valid credentials returns tokens."""
    await _register(client)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]


async def test_login_wrong_password(client: AsyncClient) -> None:
    """Login with wrong password returns 401."""
    await _register(client)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword1"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """Login with nonexistent email returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "somepassword1"},
    )
    assert response.status_code == 401


async def test_refresh_success(client: AsyncClient) -> None:
    """Refresh with valid refresh token returns new token pair."""
    data = await _register(client)
    refresh_token = data["data"]["refresh_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]


async def test_refresh_with_access_token_fails(client: AsyncClient) -> None:
    """Refresh with access token (wrong type) returns 401."""
    data = await _register(client)
    access_token = data["data"]["access_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


async def test_me_authenticated(client: AsyncClient) -> None:
    """GET /me with valid token returns user info."""
    data = await _register(client)
    access_token = data["data"]["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["email"] == "test@example.com"
    assert body["data"]["id"]


async def test_me_unauthenticated(client: AsyncClient) -> None:
    """GET /me without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


async def test_me_expired_token(client: AsyncClient) -> None:
    """GET /me with expired/invalid token returns 401."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
