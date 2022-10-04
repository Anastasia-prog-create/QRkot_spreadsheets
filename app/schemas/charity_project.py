from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt, validator


class CharityProjectBase(BaseModel):
    class Config:
        min_anystr_length = 1
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., max_length=100)
    description: str
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str]
    full_amount: Optional[PositiveInt]

    @validator('name', 'full_amount')
    def value_cannot_be_null(cls, value):
        if value is None:
            raise ValueError(
                'Значение null не допустимо!'
            )
        return value


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class CharityProjectGoogle(BaseModel):
    name: str
    description: str
