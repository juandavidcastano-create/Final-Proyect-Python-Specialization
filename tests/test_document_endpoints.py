import tempfile
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.dependencies.document import get_document_service
from app.dependencies.project import get_project_service

client = TestClient(app)


class DummyDocumentService:
    def __init__(self, result=None, exception=None, document=None, file_path=None):
        self._result = result
        self._exception = exception
        self._document = document
        self._file_path = file_path

    def create_document_from_upload(self, upload_file, project_id, owner_id):
        if self._exception:
            raise self._exception
        return self._result

    def get_document_by_id(self, document_id):
        if self._exception:
            raise self._exception
        return self._document

    def get_document_file_path(self, document_id):
        if self._exception:
            raise self._exception
        return self._file_path

    def get_document_file_content(self, document_id):
        if self._exception:
            raise self._exception
        if self._file_path is None:
            raise ValueError("Document file not found")

        if hasattr(self._file_path, "read_bytes"):
            if not self._file_path.exists():
                raise ValueError("Document file not found")
            return self._file_path.read_bytes()

        if not Path(self._file_path).exists():
            raise ValueError("Document file not found")

        with open(self._file_path, "rb") as f:
            return f.read()

    def delete_document_file(self, document_id):
        if self._exception:
            raise self._exception
        return True

    def delete_document(self, document_id):
        if self._exception:
            raise self._exception
        return self._result

    def list_documents_by_project(self, project_id):
        if self._exception:
            raise self._exception
        return self._result


class DummyProjectService:
    def __init__(self, project=None):
        self.project = project

    def get_project_info(self, project_id, user_id):
        return self.project

    def _verify_project_access(self, project_id, user_id):
        return True

    def verify_project_owner(self, project_id, user_id):
        return True


def override_dependency(dependency, value):
    def _override():
        return value
    return _override


def test_attach_document_to_project_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(result={
            "id": 1,
            "file_name": "example.txt",
            "s3_key": "projects/1/example.txt",
            "size": 11,
            "project_id": 1,
        }),
    )

    response = client.post(
        "/projects/1/documents",
        files={"file": ("example.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "file_name": "example.txt",
        "s3_key": "projects/1/example.txt",
        "size": 11,
        "project_id": 1,
    }

    app.dependency_overrides.clear()


def test_download_document_success():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "example.txt"
        path.write_bytes(b"hello world")

        document = SimpleNamespace(
            project_id=1,
            file_name="example.txt",
            dir=str(tmp_dir),
        )

        app.dependency_overrides[get_current_user] = override_dependency(
            get_current_user,
            SimpleNamespace(id=1, email="alice@example.com"),
        )
        app.dependency_overrides[get_project_service] = override_dependency(
            get_project_service,
            DummyProjectService(project=document),
        )
        app.dependency_overrides[get_document_service] = override_dependency(
            get_document_service,
            DummyDocumentService(document=document, file_path=path),
        )

        response = client.get("/document/1")

        assert response.status_code == 200
        assert response.content == b"hello world"
        assert response.headers["content-disposition"].startswith("attachment;")

        app.dependency_overrides.clear()


def test_update_document_success():
    document = SimpleNamespace(
        id=1,
        project_id=1,
        file_name="example.txt",
        dir="C:\\temp",
    )

    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=document),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(result={
            "id": 1,
            "file_name": "updated_example.txt",
            "s3_key": "projects/1/updated_example.txt",
            "size": 12,
            "project_id": 1,
        }, document=document),
    )

    response = client.put(
        "/document/1",
        files={"file": ("updated_example.txt", b"hello updated", "text/plain")},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "file_name": "updated_example.txt",
        "s3_key": "projects/1/updated_example.txt",
        "size": 12,
        "project_id": 1,
    }

    app.dependency_overrides.clear()


def test_delete_document_success():
    document = SimpleNamespace(
        id=1,
        project_id=1,
        file_name="example.txt",
        dir="C:\\temp",
    )

    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=document),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(document=document, result=None),
    )

    response = client.delete("/document/1")

    assert response.status_code == 204
    assert response.text == ""

    app.dependency_overrides.clear()


def test_list_project_documents_success():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(result=[
            {"id": 1, "file_name": "example.txt", "s3_key": "projects/1/example.txt", "size": 11, "project_id": 1}
        ]),
    )

    response = client.get("/projects/1/documents")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "file_name": "example.txt", "s3_key": "projects/1/example.txt", "size": 11, "project_id": 1}
    ]

    app.dependency_overrides.clear()


def test_attach_document_duplicate_conflict():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(exception=ValueError("Document 'example.txt' already exists")),
    )

    response = client.post(
        "/projects/1/documents",
        files={"file": ("example.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "A document with the same name already exists in this project"}

    app.dependency_overrides.clear()


def test_download_document_not_found():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(document=None),
    )

    response = client.get("/document/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


def test_download_document_file_missing():
    document = SimpleNamespace(project_id=1, file_name="example.txt", dir="C:\\temp")

    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=document),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(document=document, file_path=Path("C:\\does_not_exist.txt")),
    )

    response = client.get("/document/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document file not found in S3"}

    app.dependency_overrides.clear()


def test_delete_document_not_found():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(document=None),
    )

    response = client.delete("/document/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


def test_list_project_documents_empty():
    app.dependency_overrides[get_current_user] = override_dependency(
        get_current_user,
        SimpleNamespace(id=1, email="alice@example.com"),
    )
    app.dependency_overrides[get_project_service] = override_dependency(
        get_project_service,
        DummyProjectService(project=SimpleNamespace(id=1)),
    )
    app.dependency_overrides[get_document_service] = override_dependency(
        get_document_service,
        DummyDocumentService(result=[]),
    )

    response = client.get("/projects/1/documents")

    assert response.status_code == 200
    assert response.json() == []

    app.dependency_overrides.clear()
