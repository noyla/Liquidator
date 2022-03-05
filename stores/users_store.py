from db.engine import session, engine
from models.db.user import User
from models.db.user_reserve_data import UserReserveData
from sqlalchemy import text, insert

class UsersStore:
    @staticmethod
    def create_user_reserves(user_reserves: list[UserReserveData]):
        session.add_all(user_reserves)
    
    @staticmethod
    def create_users(users: list[User]):
        session.add_all(users)
    
    @staticmethod
    def create_users_with_reserves(users: list[User], 
                user_reserves: list[UserReserveData]):
        users = [u.to_dict() for u in users.values()]
        # user_reserves = [u.to_dict() for u in user_reserves]
        stmt = insert(User).values(users).prefix_with('IGNORE')
        # no_update_stmt = stmt.
        # compiled = stmt.compile()
        with engine.connect() as conn:
            res = conn.execute(stmt)
            # conn.commit()


            # conn.execute(text(f"INSERT INTO {User.__tablename__}") VALUES {values}"
            # , {"some_private_name": "pii"})
