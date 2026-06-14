from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repository.document import DocumentRepository
from app.services.documet import DocumentService

#Todo:
def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository, db)
