from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.user import get_user_service

client = TestClient(app)


class DummyUserService:
    def __init__(self, result=None, exception=None):
        self._result = result
        self._exception = exception

    def create_user(self, user_create):
        if self._exception:
            raise self._exception
        return self._result

    def login(self, email: str, password: str):
        if self._exception:
            raise self._exception
        return self._result


def override_user_service(user_service):
    def _override():
        return user_service
    return _override


def test_create_user_success():
    app.dependency_overrides[get_user_service] = override_user_service(
        DummyUserService(result={"id": 1, "email": "juan@example.com"})
    )

    response = client.post(
        "/users/auth",
        json={"email": "juan@example.com", "password": "securepass", "repeated_password": "securepass"},
    )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "juan@example.com"}

    app.dependency_overrides.clear()


def test_create_user_conflict():
    app.dependency_overrides[get_user_service] = override_user_service(
        DummyUserService(
            exception=HTTPException(status_code=400, detail="Email already registered")
        )
    )

    response = client.post(
        "/users/auth",
        json={"email": "bob@example.com", "password": "secret123", "repeated_password": "secret123"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

    app.dependency_overrides.clear()


def test_login_success():
    app.dependency_overrides[get_user_service] = override_user_service(
        DummyUserService(result={"access_token": "token", "token_type": "bearer"})
    )

    response = client.post(
        "/users/login",
        json={"email": "juan@example.com", "password": "securepass"},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": "token", "token_type": "bearer"}

    app.dependency_overrides.clear()


def test_login_invalid_credentials():
    app.dependency_overrides[get_user_service] = override_user_service(
        DummyUserService(
            exception=HTTPException(
                status_code=401,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        )
    )

    response = client.post(
        "/users/login",
        json={"email": "unknown@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

    app.dependency_overrides.clear()


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Project Dashboard API is running."}


def test_create_user_password_mismatch():
    response = client.post(
        "/users/auth",
        json={"email": "alice@example.com", "password": "pass1", "repeated_password": "pass2"},
    )

    assert response.status_code == 422
    assert any(
        detail.get("msg") == "Value error, Passwords do not match"
        for detail in response.json()["detail"]
    )


def test_create_user_invalid_email():
    response = client.post(
        "/users/auth",
        json={"email": "invalid-email", "password": "pass123", "repeated_password": "pass123"},
    )

    assert response.status_code == 422
    assert any(
        detail.get("loc") == ["body", "email"] and "valid email address" in detail.get("msg", "")
        for detail in response.json()["detail"]
    )

def test_login_missing_fields():
    response = client.post(
        "/users/login",
        json={"email": "juan@example.com"},
    )

    assert response.status_code == 422
    app.dependency_overrides.clear()
