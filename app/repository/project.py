from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user_project import UserProject
from app.repository.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def get_project_by_id(self, project_id: int) -> Project:
        return self.get_by_id(project_id)

    def create_project(self, *, name: str, description: str, created_at: str, user_id: int):
        project = self.create(name=name, description=description, created_at=created_at)
        user_project = UserProject(user_id=user_id, project_id=project.id, role="owner")
        self.db.add(user_project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project_id: int, **kwargs) -> Project:
        project = self.get_by_id(project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete_project(self, project_id: int):
        return self.delete_by_id(project_id)
    
    def list_projects_by_user(self, user_id: int):
        return (
            self.db.query(self.model)
            .join(UserProject, self.model.id == UserProject.project_id)
            .filter(UserProject.user_id == user_id)
            .all()
        )
