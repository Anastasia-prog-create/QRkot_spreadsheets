from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CharityProjectCRUD(CRUDBase):

    async def get_project_by_name(
        self,
        name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == name
            )
        )
        return db_project.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        collection_time = (
            (func.julianday(CharityProject.close_date) -
             func.julianday(CharityProject.create_date)) * 24 * 60 * 60
        )
        projects = await session.execute(
            select([
                CharityProject.name,
                collection_time.label('collection_time'),
                CharityProject.description
            ]).where(
                CharityProject.fully_invested
            ).order_by(
                collection_time
            )
        )
        return projects.all()


charity_project_crud = CharityProjectCRUD(CharityProject)
