from db.engine import session
from models.db.user_reserve_data import UserReserveData

class UserReserveStore:
    @staticmethod
    def create(user_reserve: UserReserveData):
        session.add(user_reserve)