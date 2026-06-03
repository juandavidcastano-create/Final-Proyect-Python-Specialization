from typing import List

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService, get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse], summary="Listar proyectos de un usuario")
def list_projects_by_user(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Listar todos los proyectos asociados a un usuario."""
    return project_service.list_projects_by_user(current_user.id)

@router.post("/create-project", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Crear proyecto")
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Crear un nuevo proyecto."""
    return project_service.create_project(project, current_user.id)

@router.put("/{project_id}", response_model=ProjectResponse, summary="Actualizar proyecto")
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Actualizar un proyecto solo si el usuario es owner."""
    return project_service.update_project(project_id, project_update, current_user.id)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar proyecto")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Eliminar un proyecto solo si el usuario es owner."""
    project_service.delete_project(project_id, current_user.id)
    return None


