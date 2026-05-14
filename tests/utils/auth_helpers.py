from fastapi.testclient import TestClient


def register_user(
        client: TestClient,
        email: str = "test@example.com",
        password: str = "password"    
):
    return client.post("/auth/register", json={
        "email": email,
        "password": password,
        "password_repeat": password,
        "first_name": "Test",
        "last_name": "User",
        "birth_date": "2000-01-01"
    })


def login_user(
        client: TestClient,
        email: str = "test@example.com",
        password: str = "password"
):
    return client.post("/auth/login", data={
        "username": email,
        "password": password
    })


def get_access_token(client: TestClient) -> str:
    register_user(client=client)
    response = login_user(client=client)
    return response.json()["access_token"]

def auth_header(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}"
    }