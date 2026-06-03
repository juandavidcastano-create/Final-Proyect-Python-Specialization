from datetime import date

from pydantic import BaseModel, model_validator

class ProjectCreate(BaseModel):
    name: str
    description: str
    created_at: date

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: date

    class Config:
        from_attributes = True

