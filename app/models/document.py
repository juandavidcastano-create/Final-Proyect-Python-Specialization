from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    s3_key = Column(String(255), nullable=False)  # S3 object key (s3://bucket/owner_id/project_id/file_name)
    size = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)

    project = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, file_name={self.file_name!r}, s3_key={self.s3_key!r}, size={self.size}, project_id={self.project_id})>"