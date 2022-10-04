from sqlalchemy import Column, ForeignKey, Integer, Text

from .base_model import DonationProjectBase


class Donation(DonationProjectBase):
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(Text)

    def __repr__(self):
        return (
            f'Пожертвование пользователя {self.user_id}: ' + super().__repr__()
        )
