"""Repository for project persistence."""
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    """Encapsulates database access for projects."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_projects(self) -> List[Project]:
        result = await self.db.execute(select(Project).order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    async def get_project(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.name == name))
        return result.scalar_one_or_none()

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update(self, project: Project, fields: Sequence[tuple[str, object]]) -> Project:
        for attr, value in fields:
            setattr(project, attr, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()
