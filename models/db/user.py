from db.engine import Base
from sqlalchemy import Column, String, Integer, DateTime, TIMESTAMP
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import column_property

class User(Base):
    __tablename__ = 'users'

    def __init__(self, id, total_collateral_eth, total_debt_eth, available_borrows_eth,
    current_liquidation_threshold, ltv, health_factor):
         self.id = id
         self.total_collateral_eth = total_collateral_eth
         self.total_debt_eth = total_debt_eth
         self.available_borrows_eth = available_borrows_eth
         self.current_liquidation_threshold = current_liquidation_threshold
         self.ltv = ltv
         self.health_factor = health_factor

    id = Column(String(50), primary_key=True)
    total_collateral_eth = Column(String(40))
    total_debt_eth = Column(String(40))
    available_borrows_eth = Column(String(40))
    current_liquidation_threshold = Column(Integer)
    ltv = Column(Integer)
    health_factor = Column(String(90), index=True)
    created_at = Column(TIMESTAMP, info={"exclude_has_default": True})

    @staticmethod
    def from_dict(user: dict):
        return User(id=user['id'], total_collateral_eth=user['total_collateral_eth'],
        total_debt_eth=user['total_debt_eth'], available_borrows_eth=user['available_borrows_eth'],
        current_liquidation_threshold=user['current_liquidation_threshold'],
        ltv=user['ltv'], health_factor=user['health_factor'])
    
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            field = getattr(self, column.name)
            if field is None:
                d[column.name] = ''
            elif str(field) in ['True', 'False', 'true', 'false']:
                d[column.name] = bool(field)
            else:
                d[column.name] = str(field)

        return d
    
    @classmethod
    def _remove_created_at(cls, user: dict):
        user.pop('created_at', None)
        return user
    
    @staticmethod
    def upsert(users):
        users = [User._remove_created_at(u) for u in users]
        insert_stmt = insert(User).values(users)
        table = User.metadata.tables[User.__tablename__]
        primKeyColNames = [pk_column.name for pk_column in table.primary_key.columns.values()]
        updatedColNames = [column.name for column in table.columns 
                           if (column.name not in [primKeyColNames, 'created_at'])]
        onDuplicate = {colName:getattr(insert_stmt.inserted, colName) for colName in updatedColNames}
        return insert_stmt.on_duplicate_key_update(onDuplicate)