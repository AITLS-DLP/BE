"""Use cases for project management."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService


class ProjectUseCase:
    """Expose project operations to the API layer."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.service = ProjectService(db)

    async def list_projects(self) -> list[ProjectRead]:
        projects = await self.service.list_projects()
        return [ProjectRead.model_validate(project) for project in projects]

    async def get_project(self, project_id: int) -> ProjectRead | None:
        project = await self.service.get_project(project_id)
        return ProjectRead.model_validate(project) if project else None

    async def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project = await self.service.create_project(payload)
        return ProjectRead.model_validate(project)

    async def update_project(self, project_id: int, payload: ProjectUpdate) -> ProjectRead | None:
        project = await self.service.update_project(project_id, payload)
        return ProjectRead.model_validate(project) if project else None

    async def delete_project(self, project_id: int) -> bool:
        return await self.service.delete_project(project_id)
