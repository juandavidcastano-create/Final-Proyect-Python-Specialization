from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

class DocumentService:
    def __init__(self, db: Session = None):
        self.db = db
    
    def create_document(self, file_name: str, dir: str, size: int, project_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.create_document(file_name=file_name, dir=dir, size=size, project_id=project_id)

    def create_document_from_upload(self, upload_file: UploadFile, project_id: int, owner_id: int):
        from app.repository.document import DocumentRepository

        file_name = Path(upload_file.filename).name

        storage_dir = Path(r"C:\Users\juand\Documents\epam_final_project") / "uploaded_documents" / str(owner_id) / str(project_id)
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_path = storage_dir / file_name
        
        if file_path.exists():
            raise ValueError(f"Document '{file_name}' already exists")

        content = upload_file.file.read()

        file_path.write_bytes(content)

        dir_path = str(storage_dir)
        document_repository = DocumentRepository(self.db)
        return document_repository.create_document(
            file_name=file_name,
            dir=dir_path,
            size=len(content),
            project_id=project_id,
        )
    
    def get_document_by_id(self, document_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.get_document_by_id(document_id)
    
    def delete_document(self, document_id: int):
        from app.repository.document import DocumentRepository
        import os

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            return None

        # Remove file from storage if exists
        file_path = Path(document.dir) / document.file_name
        try:
            if file_path.exists():
                os.remove(file_path)
        except OSError as exc:
            raise ValueError(f"Failed to delete document file: {exc}")

        return document_repository.delete_document(document_id)

    def get_document_file_path(self, document_id: int):
        """Return Path to the stored file for a document id, or None if document not found."""
        from app.repository.document import DocumentRepository

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            return None
        return Path(document.dir) / document.file_name

    def delete_document_file(self, document_id: int):
        """Delete only the file associated with a document (keeps DB record)."""
        from app.repository.document import DocumentRepository
        import os

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            return None

        file_path = Path(document.dir) / document.file_name
        try:
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except OSError as exc:
            raise ValueError(f"Failed to delete document file: {exc}")
    
    def list_documents_by_project(self, project_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.list_documents_by_project(project_id)
    
