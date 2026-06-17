from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.dependencies.project import get_project_service

client = TestClient(app)


class DummyProjectService:
    def __init__(self, result=None, exception=None):
        self._result = result
        self._exception = exception

    def create_project(self, project_create, user_id):
        if self._exception:
            raise self._exception
        return self._result

    def list_projects_by_user(self, user_id):
        if self._exception:
            raise self._exception
        return self._result

    def get_project_info(self, project_id, user_id):
        if self._exception:
            raise self._exception
        return self._result

    def update_project(self, project_id, project_update, user_id):
        if self._exception:
            raise self._exception
        return self._result

    def delete_project(self, project_id, user_id):
        if self._exception:
            raise self._exception
        return self._result

    def add_collaborator(self, project_id, collaborator_email, user_id):
        if self._exception:
            raise self._exception
        return self._result


def override_dependency(dependency, value):
    def _override():
        return value
    return _override


def test_create_project_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result={"id": 1, "name": "Test Project", "description": "A sample project", "created_at": "2026-06-13", "role": "owner"}),
    )

    response = client.post(
        "/projects/create-project",
        json={"name": "Test Project", "description": "A sample project"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Test Project",
        "description": "A sample project",
        "created_at": "2026-06-13",
        "role": "owner",
    }

    app.dependency_overrides.clear()


def test_list_projects_by_user_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result=[
            {"id": 1, "name": "Test Project", "description": "A sample project", "created_at": "2026-06-13", "role": "owner"}
        ]),
    )

    response = client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Test Project", "description": "A sample project", "created_at": "2026-06-13", "role": "owner"}
    ]

    app.dependency_overrides.clear()


def test_get_project_info_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result={"id": 1, "name": "Test Project", "description": "A sample project", "created_at": "2026-06-13", "role": "owner"}),
    )

    response = client.get("/projects/1/info")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Test Project",
        "description": "A sample project",
        "created_at": "2026-06-13",
        "role": "owner",
    }

    app.dependency_overrides.clear()


def test_update_project_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result={"id": 1, "name": "Updated Project", "description": "Updated description", "created_at": "2026-06-13", "role": "owner"}),
    )

    response = client.put(
        "/projects/1",
        json={"name": "Updated Project", "description": "Updated description"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Updated Project",
        "description": "Updated description",
        "created_at": "2026-06-13",
        "role": "owner",
    }

    app.dependency_overrides.clear()


def test_delete_project_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result=None),
    )

    response = client.delete("/projects/1")

    assert response.status_code == 204
    assert response.text == ""

    app.dependency_overrides.clear()


def test_add_collaborator_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result={"id": 1, "name": "Test Project", "description": "A sample project", "created_at": "2026-06-13", "role": "owner"}),
    )

    response = client.post("/projects/1/invite/?user=bob%40example.com")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Test Project",
        "description": "A sample project",
        "created_at": "2026-06-13",
        "role": "owner",
    }

    app.dependency_overrides.clear()


def test_list_projects_by_user_empty():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(result=[]),
    )

    response = client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == []

    app.dependency_overrides.clear()


def test_get_project_info_forbidden():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(
            exception=HTTPException(status_code=403, detail="You do not have access to this project")
        ),
    )

    response = client.get("/projects/1/info")

    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to this project"}

    app.dependency_overrides.clear()


def test_update_project_not_found():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(
            exception=HTTPException(status_code=404, detail="Project not found")
        ),
    )

    response = client.put(
        "/projects/1",
        json={"name": "Updated Project", "description": "Updated description"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

    app.dependency_overrides.clear()


def test_delete_project_forbidden():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(
            exception=HTTPException(status_code=403, detail="Only project owner can delete this project")
        ),
    )

    response = client.delete("/projects/1")

    assert response.status_code == 403
    assert response.json() == {"detail": "Only project owner can delete this project"}

    app.dependency_overrides.clear()


def test_add_collaborator_forbidden():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(
            exception=HTTPException(status_code=403, detail="Only project owner can add collaborators")
        ),
    )

    response = client.post("/projects/1/invite/?user=bob%40example.com")

    assert response.status_code == 403
    assert response.json() == {"detail": "Only project owner can add collaborators"}

    app.dependency_overrides.clear()
