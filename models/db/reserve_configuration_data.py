from operator import lt
from db.engine import Base
from sqlalchemy import Column, String, Integer, Boolean

class Reserve(Base):
    __tablename__ = 'reserves'

    name = Column(String, primary_key=True)
    address = Column(String)
    decimals = Column(Integer)
    ltv = Column(Integer) # loan to value
    liquidation_threshold = Column(Integer)
    liquidation_bonus = Column(Integer)
    reserve_factor = Column(Integer) # reserve interest 
    usage_as_collateral_enabled = Column(Boolean)
    borrowing_enabled = Column(Boolean)
    stableborrow_rate_enabled = Column(Boolean)
    is_active = Column(Boolean)
    is_frozen = Column(Boolean)

    def __init__(self, decimals, ltv, liquidation_threshold,
        liquidation_bonus, reserve_factor, usage_as_collateral_enabled, 
        borrowing_enabled, stableborrow_rate_enabled, is_active, is_frozen, 
        name, address='') -> None:
        super().__init__()
        self.name = name
        self.address = address
        self.decimals = decimals
        self.ltv = ltv # loan to value
        self.liquidation_threshold = liquidation_threshold
        self.liquidation_bonus = liquidation_bonus
        self.reserve_factor = reserve_factor # reserve interest 
        self.usage_as_collateral_enabled = usage_as_collateral_enabled
        self.borrowing_enabled = borrowing_enabled
        self.stableborrow_rate_enabled = stableborrow_rate_enabled
        self.is_active = is_active
        self.is_frozen = is_frozen


    @staticmethod
    def from_raw_list(user_data: list):
        res = {}
        # for i, v in enumerate(user_data):
        #     res[RESERVE_CONFIGURATION_DATA[i]] = v
        # res = list(res.values())
        return Reserve(decimals=user_data[0],ltv=user_data[1], 
            liquidation_threshold=user_data[2], liquidation_bonus=user_data[3], 
            reserve_factor=user_data[4], usage_as_collateral_enabled=user_data[5], 
            borrowing_enabled=user_data[6], stableborrow_rate_enabled=user_data[7], 
            is_active=user_data[8], is_frozen=user_data[9], 
            name=user_data[10], address=user_data[11])