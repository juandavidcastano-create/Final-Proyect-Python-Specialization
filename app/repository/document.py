from sqlalchemy.orm import Session

from app.repository.base import BaseRepository

class DocumentRepository(BaseRepository):
    def __init__(self, db: Session):
        from app.models.document import Document
        super().__init__(db, Document)

    def create_document(self, file_name: str, s3_key: str, size: int, project_id: int):
        return super().create(
            file_name=file_name,
            s3_key=s3_key,
            size=size,
            project_id=project_id
        )

    def get_document_by_id(self, document_id: int):
        return super().get_by_id(document_id)
    
    def delete_document(self, document_id: int):
        return super().delete_by_id(document_id)
    
    def list_documents_by_project(self, project_id: int):
        return self.db.query(self.model).filter(self.model.project_id == project_id).all()

    def delete_documents_by_project(self, project_id: int):
        deleted_count = self.db.query(self.model).filter(self.model.project_id == project_id).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count

    def get_document_by_name_and_project(self, file_name: str, project_id: int):
        return self.db.query(self.model).filter(
        self.model.file_name == file_name,
        self.model.project_id == project_id
    ).first()