from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

from app.dependencies.auth import get_current_user
from app.dependencies.document import get_document_service
from app.dependencies.project import get_project_service
from app.schemas.document import DocumentResponse
from app.services.project import ProjectService

router = APIRouter(tags=["documents"])


@router.post("/projects/{project_id}/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
def attach_document_to_project(
    project_id: int,
    file: UploadFile = File(...),
    document_service=Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user=Depends(get_current_user),
):
    # Verificar acceso a proyecto (owner o colaborador)
    project_service.get_project_info(project_id, current_user.id)

    try:
        return document_service.create_document_from_upload(file, project_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A document with the same name already exists in this project"
        )


@router.get("/document/{document_id}", status_code=status.HTTP_200_OK, response_model=DocumentResponse)
def download_document(
    document_id: int,
    document_service=Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user=Depends(get_current_user),
):
    document = document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verificar que el usuario tiene acceso al proyecto
    project_service.get_project_info(document.project_id, current_user.id)

    # Obtener ruta al archivo desde el servicio y retornarlo
    file_path = document_service.get_document_file_path(document_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")

    return FileResponse(path=str(file_path), filename=document.file_name)

@router.put("/document/{document_id}", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
def update_document(
    document_id: int,
    file: UploadFile = File(...),
    document_service=Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user=Depends(get_current_user),
):
    document = document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verificar que el usuario es owner del proyecto
    project_service._verify_project_access(document.project_id, current_user.id)

    # Eliminar el archivo anterior usando el servicio
    try:
        document_service.delete_document_file(document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete the existing document file"
        )

    # Guardar el nuevo archivo y actualizar la información del documento
    return document_service.create_document_from_upload(file, document.project_id, current_user.id)


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    document_service=Depends(get_document_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user=Depends(get_current_user),
):
    document = document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Solo el owner del proyecto puede eliminar el documento
    project_service.verify_project_owner(document.project_id, current_user.id)

    try:
        document_service.delete_document(document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    return None

