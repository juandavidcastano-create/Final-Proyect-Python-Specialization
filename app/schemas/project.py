from datetime import date

from pydantic import BaseModel, model_validator

class ProjectCreate(BaseModel):
    name: str
    description: str
    created_at: date | None = date.today()

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: date | None = None
    role: str | None = None

    class Config:
        from_attributes = True

