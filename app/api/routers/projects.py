"""Project management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.usecases.project_usecases import ProjectUseCase

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectRead], summary="프로젝트 목록 조회")
async def list_projects(usecase: ProjectUseCase = Depends()) -> List[ProjectRead]:
    return await usecase.list_projects()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, summary="프로젝트 생성")
async def create_project(payload: ProjectCreate, usecase: ProjectUseCase = Depends()) -> ProjectRead:
    try:
        return await usecase.create_project(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}", response_model=ProjectRead, summary="프로젝트 상세 조회")
async def get_project(project_id: int, usecase: ProjectUseCase = Depends()) -> ProjectRead:
    project = await usecase.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead, summary="프로젝트 수정")
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    usecase: ProjectUseCase = Depends(),
) -> ProjectRead:
    try:
        project = await usecase.update_project(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="프로젝트 삭제")
async def delete_project(project_id: int, usecase: ProjectUseCase = Depends()) -> None:
    deleted = await usecase.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
