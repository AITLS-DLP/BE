"""
User Repository
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash


class UserRepository:
    """사용자 데이터 접근 레이어"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
            self,
            username: str,
            email: str,
            password: str,
            full_name: str | None = None
    ) -> User:
        """사용자 생성"""
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=False
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
