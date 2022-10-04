from sqlalchemy import Column, String, Text

from .base_model import DonationProjectBase


class CharityProject(DonationProjectBase):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (f'Проект "{self.name}" ' + super().__repr__())
