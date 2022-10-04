from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_before_delete, check_before_update,
                                check_full_amount_update, check_name_duplicate,
                                check_project_exists)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session)
) -> list[CharityProject]:
    """Доступно для всех пользователей."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
) -> CharityProject:
    """Только для суперюзеров, создание нового проекта."""
    await check_name_duplicate(project.name, session)
    project = await charity_project_crud.create(project, session)
    changed_objects, project = await investment_process(
        session=session,
        new_object=project,
    )
    session.add_all((*changed_objects, project))
    await session.commit()
    await session.refresh(project)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> CharityProject:
    """Только для суперюзеров и проектов без инвестиций."""
    project = await charity_project_crud.get(project_id, session)
    await check_before_delete(project)
    await charity_project_crud.remove(project, session)
    return project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    '''Только для суперюзеров и активных проектов.'''
    old_project = await check_project_exists(
        project_id,
        session
    )
    await check_before_update(old_project)
    if project_data.full_amount is not None:
        check_full_amount_update(
            old_project,
            project_data.full_amount,
        )
    if project_data.name is not None:
        await check_name_duplicate(
            project_data.name,
            session
        )
    project_update = await charity_project_crud.update(
        old_project,
        project_data,
        session
    )
    return project_update
