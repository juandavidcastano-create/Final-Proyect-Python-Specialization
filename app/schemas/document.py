from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    file_name: str
    s3_key: str
    size: int
    project_id: int

    class Config:
        from_attributes = True
