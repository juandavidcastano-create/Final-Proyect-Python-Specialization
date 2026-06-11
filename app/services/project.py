from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repository.project import ProjectRepository
from app.models.user_project import UserProject

class ProjectService:
    def __init__(self, project_repository: ProjectRepository, db: Session = None):
        self.project_repository = project_repository
        self.db = db
    
    def verify_project_owner(self, project_id: int, user_id: int, raise_on_error: bool = True):
        """Verifica si el usuario es owner del proyecto.

        Si `raise_on_error` es True lanza HTTPException en caso de no existir el proyecto
        o de no ser owner. Si es False, devuelve False en esos casos.
        """
        if not self.db:
            if raise_on_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only project owner can perform this action",
                )
            return False

        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            if raise_on_error:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )
            return False

        user_project = self.db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
            UserProject.role == "owner",
        ).first()
        if not user_project:
            if raise_on_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only project owner can perform this action",
                )
            return False

        return project if raise_on_error else True

    def _verify_project_access(self, project_id: int, user_id: int) -> bool:
        """Verifica si el usuario tiene acceso al proyecto (owner o collaborator)."""
        if not self.db:
            return False
        
        user_project = self.db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id
        ).first()
        return user_project is not None

    def _serialize_project(self, project, user_id: int) -> dict:
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "role": self.project_repository.get_user_project_role(project.id, user_id),
        }

    def create_project(self, project_create: ProjectCreate, user_id: int):
        project = self.project_repository.create_project(
            name=project_create.name,
            description=project_create.description,
            created_at=project_create.created_at,
            user_id=user_id
        )
        return self._serialize_project(project, user_id)

    def update_project(self, project_id: int, project_update: ProjectUpdate, user_id: int):
        if not self._verify_project_access(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update this project"
            )
        project = self.project_repository.update_project(project_id, **project_update.dict(exclude_unset=True))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return self._serialize_project(project, user_id)

    def delete_project(self, project_id: int, user_id: int):
        if not self.verify_project_owner(project_id, user_id, raise_on_error=False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete this project"
            )

        self._delete_project_storage_folder(user_id, project_id)
        self._delete_project_documents_from_db(project_id)

        return self.project_repository.delete_project(project_id)

    def _delete_project_storage_folder(self, owner_id: int, project_id: int):
        storage_root = Path(r"C:\Users\juand\Documents\epam_final_project") / "uploaded_documents"
        project_folder = storage_root / str(owner_id) / str(project_id)
        if project_folder.exists() and project_folder.is_dir():
            try:
                shutil.rmtree(project_folder)
            except OSError as exc:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete project document folder: {exc}",
                )

    def _delete_project_documents_from_db(self, project_id: int):
        from app.repository.document import DocumentRepository

        document_repository = DocumentRepository(self.db)
        document_repository.delete_documents_by_project(project_id)

    def list_projects_by_user(self, user_id: int):
        projects = self.project_repository.list_projects_by_user(user_id)
        return [self._serialize_project(project, user_id) for project in projects]

    def get_project_info(self, project_id: int, user_id: int):
        """Obtiene los detalles del proyecto si el usuario tiene acceso."""
        if not self._verify_project_access(project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project"
            )
        
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return self._serialize_project(project, user_id)
    
    def add_collaborator(self, project_id: int, collaborator_email: str, user_id: int):
        if not self.verify_project_owner(project_id, user_id, raise_on_error=False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can add collaborators"
            )
        project = self.project_repository.add_collaborator(project_id, collaborator_email)
        return self._serialize_project(project, user_id)
