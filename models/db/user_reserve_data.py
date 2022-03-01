from datetime import datetime, timezone
from db.engine import Base
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, \
    TIMESTAMP, Boolean, Sequence, DateTime


class UserReserveData(Base):
    __tablename__ = 'users_reserve_data'
    
    id = Column(String(60), primary_key=True)
    user = Column(String(50), ForeignKey('users.id'))
    reserve = Column(String(50), ForeignKey('reserves.name'))
    current_aToken_balance = Column(String(50))
    current_stable_debt = Column(String(50))
    current_variable_debt = Column(String(50))
    principal_stable_debt = Column(String(50))
    scaled_variable_debt = Column(String(50))
    stable_borrow_rate = Column(String(50))
    liquidity_rate = Column(String(50))
    stable_rate_last_updated = Column(DateTime())
    usage_as_collateral_enabled = Column(Boolean)

    def __init__(self, current_aToken_balance, current_stable_debt,
    current_variable_debt, principal_stable_debt, scaled_variable_debt, 
    stable_borrow_rate, liquidity_rate, stable_rate_last_updated, 
    usage_as_collateral_enabled, reserve, user) -> None:
        super().__init__()
        self.user = user
        self.reserve = reserve
        self.current_aToken_balance = current_aToken_balance
        self.current_stable_debt = current_stable_debt
        self.current_variable_debt = current_variable_debt
        self.principal_stable_debt = principal_stable_debt
        self.scaled_variable_debt = scaled_variable_debt
        self.stable_borrow_rate = stable_borrow_rate
        self.liquidity_rate = liquidity_rate
        self.stable_rate_last_updated = stable_rate_last_updated
        self.usage_as_collateral_enabled = usage_as_collateral_enabled

    @staticmethod
    def from_raw_list(user_data: list):
        stable_rate_last_updated = datetime.fromtimestamp(user_data[7], timezone.utc) \
            if user_data[7] else None
        
        return UserReserveData(user_data[0], user_data[1], user_data[2], user_data[3], \
            user_data[4], user_data[5], user_data[6], stable_rate_last_updated, \
            user_data[8], reserve=user_data[9], user=user_data[10])
    
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))

        return d