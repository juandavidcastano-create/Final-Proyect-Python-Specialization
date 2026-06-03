from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repository.project import ProjectRepository
from app.models.user_project import UserProject
from app.db.database import get_db

class ProjectService:
    def __init__(self, project_repository: ProjectRepository, db: Session = None):
        self.project_repository = project_repository
        self.db = db
    
    def _verify_project_owner(self, project_id: int, user_id: int) -> bool:
        """Verifica si el usuario es owner del proyecto."""
        if not self.db:
            return False
        
        user_project = self.db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
            UserProject.role == "owner"
        ).first()
        return user_project is not None

    def create_project(self, project_create: ProjectCreate, user_id: int):
        return self.project_repository.create_project(
            name=project_create.name,
            description=project_create.description,
            created_at=project_create.created_at,
            user_id=user_id
        )

    def update_project(self, project_id: int, project_update: ProjectUpdate, user_id: int):
        if not self._verify_project_owner(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update this project"
            )
        return self.project_repository.update_project(project_id, **project_update.dict(exclude_unset=True))

    def delete_project(self, project_id: int, user_id: int):
        if not self._verify_project_owner(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete this project"
            )
        return self.project_repository.delete_project(project_id)

    def list_projects_by_user(self, user_id: int):
        return self.project_repository.list_projects_by_user(user_id)


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    repository = ProjectRepository(db)
    return ProjectService(repository, db)