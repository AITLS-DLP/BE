"""Business logic for project management."""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Coordinates project related operations."""

    def __init__(self, db: AsyncSession):
        self.repository = ProjectRepository(db)

    async def list_projects(self) -> List[Project]:
        return await self.repository.list_projects()

    async def get_project(self, project_id: int) -> Optional[Project]:
        return await self.repository.get_project(project_id)

    async def create_project(self, payload: ProjectCreate) -> Project:
        existing = await self.repository.get_by_name(payload.name)
        if existing:
            raise ValueError("Project name already exists")
        project = Project(
            name=payload.name,
            description=payload.description,
            owner=payload.owner,
            status=payload.status,
        )
        return await self.repository.create(project)

    async def update_project(self, project_id: int, payload: ProjectUpdate) -> Optional[Project]:
        project = await self.repository.get_project(project_id)
        if project is None:
            return None
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            existing = await self.repository.get_by_name(updates["name"])
            if existing and existing.id != project_id:
                raise ValueError("Project name already exists")
        fields = list(updates.items())
        if not fields:
            return project
        return await self.repository.update(project, fields)

    async def delete_project(self, project_id: int) -> bool:
        project = await self.repository.get_project(project_id)
        if project is None:
            return False
        await self.repository.delete(project)
        return True
