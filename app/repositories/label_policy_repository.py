"""Repository for label policy persistence."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label_policy import LabelPolicy


class LabelPolicyRepository:
    """Provides CRUD operations for label policies."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_policies(self) -> List[LabelPolicy]:
        result = await self.db.execute(select(LabelPolicy).order_by(LabelPolicy.label.asc()))
        return list(result.scalars().all())

    async def get_by_label(self, label: str) -> Optional[LabelPolicy]:
        result = await self.db.execute(select(LabelPolicy).where(LabelPolicy.label == label))
        return result.scalar_one_or_none()

    async def upsert(self, label: str, block: bool, updated_by: Optional[str] = None) -> LabelPolicy:
        policy = await self.get_by_label(label)
        if policy is None:
            policy = LabelPolicy(label=label, block=block, updated_by=updated_by)
            self.db.add(policy)
        else:
            policy.block = block
            if updated_by is not None:
                policy.updated_by = updated_by
        await self.db.commit()
        await self.db.refresh(policy)
        return policy
