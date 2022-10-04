from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class UserDonations(DonationCreate):
    id: int
    create_date: datetime


class DonationDB(UserDonations):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
