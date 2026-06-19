from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.s3_service import S3Service

class DocumentService:
    def __init__(self,document_repository,db: Session = None):
        self.db = db
        self.s3_service = S3Service()
    
    def create_document(self, file_name: str, s3_key: str, size: int, project_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.create_document(file_name=file_name, s3_key=s3_key, size=size, project_id=project_id)

    def create_document_from_upload(self, upload_file: UploadFile, project_id: int, owner_id: int):
        from app.repository.document import DocumentRepository

        file_name = upload_file.filename
        content = upload_file.file.read()

        # Upload to S3
        s3_metadata = self.s3_service.upload_file(content, file_name, owner_id, project_id)
        
        # Check if document already exists in DB
        document_repository = DocumentRepository(self.db)
        existing = document_repository.get_document_by_name_and_project(file_name, project_id)
        if existing:
            raise ValueError(f"Document '{file_name}' already exists in this project")

        # Create document record in DB
        return document_repository.create_document(
            file_name=file_name,
            s3_key=s3_metadata["key"],
            size=s3_metadata["size"],
            project_id=project_id,
        )
    
    def get_document_by_id(self, document_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.get_document_by_id(document_id)
    
    def delete_document(self, document_id: int):
        from app.repository.document import DocumentRepository

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            return None

        # Delete file from S3
        try:
            self.s3_service.delete_file(document.s3_key)
        except ValueError as exc:
            raise ValueError(f"Failed to delete document from S3: {exc}")

        # Delete from DB
        return document_repository.delete_document(document_id)

    def get_document_file_content(self, document_id: int) -> bytes:
        """Download document file content from S3."""
        from app.repository.document import DocumentRepository

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            raise ValueError("Document not found")
        
        return self.s3_service.download_file(document.s3_key)

    def delete_document_file(self, document_id: int):
        """Delete only the file from S3 (keeps DB record)."""
        from app.repository.document import DocumentRepository

        document_repository = DocumentRepository(self.db)
        document = document_repository.get_document_by_id(document_id)
        if not document:
            return None

        try:
            self.s3_service.delete_file(document.s3_key)
            return True
        except ValueError as exc:
            raise ValueError(f"Failed to delete document file from S3: {exc}")
    
    def list_documents_by_project(self, project_id: int):
        from app.repository.document import DocumentRepository
        document_repository = DocumentRepository(self.db)
        return document_repository.list_documents_by_project(project_id)

    
