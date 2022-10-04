from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, UserDonations
from app.services.investment import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
) -> list[Donation]:
    """Только для суперюзеров."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my/',
    response_model=List[UserDonations],
    response_model_exclude_unset=True,
    dependencies=[Depends(current_user)]
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> list[Donation]:
    """Просмотр своих пожертвований."""
    donations = await donation_crud.get_by_user(
        user=user,
        session=session
    )
    return jsonable_encoder(donations)


@router.post(
    '/',
    response_model=UserDonations,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)]
)
async def create_donation(
        data: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> Donation:
    """Только для зарегистрированных пользователей."""
    donation = await donation_crud.create(
        data,
        session,
        user
    )
    changed_objects, donation = await investment_process(
        session=session,
        new_object=donation,
    )
    session.add_all((*changed_objects, donation))
    await session.commit()
    await session.refresh(donation)
    return jsonable_encoder(donation)
