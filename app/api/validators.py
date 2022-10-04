from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject

NAME_DUPLICATE = 'Проект с таким именем уже существует!'
PROJECT_NOT_FOUND = 'Проект c id={} не найден!'
PROJECT_CLOSED = 'Закрытый проект нельзя редактировать!'
PROJECT_HAS_MONEY = 'В проект были внесены средства, не подлежит удалению!'
FULL_AMOUNT_UPDATE = 'Укажите сумму большую или равную вложенной!'


async def check_name_duplicate(
        name: str,
        session: AsyncSession,
) -> None:
    room_id = await charity_project_crud.get_project_by_name(name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=400,
            detail=NAME_DUPLICATE.format(name),
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail=PROJECT_NOT_FOUND.format(id)
        )
    return project


async def check_before_update(
        project: CharityProject,
) -> None:
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail=PROJECT_CLOSED
        )


async def check_before_delete(
        project: CharityProject,
) -> None:
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=PROJECT_HAS_MONEY
        )


async def check_full_amount_update(
    old_project: CharityProject,
    full_amount: int,
) -> None:
    if full_amount > old_project.invested_amount:
        raise HTTPException(
            status_code=422,
            detail=FULL_AMOUNT_UPDATE
        )
