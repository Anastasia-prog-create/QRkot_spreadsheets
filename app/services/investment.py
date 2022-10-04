from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import Donation


def close_objects(objects: List[Base]) -> None:
    '''Закрывает объекты без свободных инвестиций.'''
    for object in objects:
        if object.full_amount == object.invested_amount:
            object.fully_invested = True
            object.close_date = datetime.now()


async def investment_process(
    new_object: Base,
    session: AsyncSession
):
    '''Процесс инвестирования.'''
    active_objects = (
        charity_project_crud if type(new_object) == Donation else
        donation_crud
    )
    all_active_objects = await active_objects.get_not_fully_invested_objects(
        session
    )
    changed_objects = []
    for object in all_active_objects:
        can_use = object.full_amount - object.invested_amount
        if can_use <= 0:
            break
        need_money = new_object.full_amount - new_object.invested_amount
        push_money = min(can_use, need_money)
        object.invested_amount += push_money
        new_object.invested_amount += push_money
        close_objects((object, new_object))
        changed_objects.append(object)
    return(changed_objects, new_object)
