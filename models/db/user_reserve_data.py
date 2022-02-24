import json
from db.engine import Base
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, \
    TIMESTAMP, Boolean


class UserReserveData(Base):
    __tablename__ = 'users_reserve_data'

    user = Column(Integer, primary_key=True)
    reserve = Column(String, ForeignKey('reserves.name'))
    current_aToken_balance = Column(BigInteger)
    current_stable_debt = Column(BigInteger)
    current_variable_debt = Column(BigInteger)
    principal_stable_debt = Column(BigInteger)
    scaled_variable_debt = Column(BigInteger)
    stable_borrow_rate = Column(Integer)
    liquidity_rate = Column(Integer)
    stable_rate_last_updated = Column(TIMESTAMP)
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
        return UserReserveData(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4],
        user_data[5], user_data[6], user_data[7], user_data[8], 
        reserve=user_data[9], user=user_data[10])
    
    def to_json(self):
        {
            
        }
        return json.dumps(self)