from db.engine import session, engine
from models.db.user import User
from models.db.user_reserve_data import UserReserveData
from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert

class UsersStore:
    @staticmethod
    def create_user_reserves(user_reserves: list[UserReserveData]):
        session.add_all(user_reserves)
    
    @staticmethod
    def create_users(users: list[User]):
        session.add_all(users)
    
    @staticmethod
    def create_users_with_reserves(users: dict[User], 
                user_reserves: list[UserReserveData]):
        users = [u.to_dict() for u in users.values()]
        user_reserves = [u.to_dict() for u in user_reserves]

        # Upsert users & user reserves
        users_stmt = User.upsert(users)
        user_reserves_stmt = UserReserveData.upsert(user_reserves)

        # compiled = stmt.compile()
        with engine.connect() as conn:
            res = conn.execute(users_stmt)
            res = conn.execute(user_reserves_stmt)

