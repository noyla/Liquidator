from sqlalchemy import Column, String
from db.engine import Base


class Settings(Base):
    __tablename__ = 'settings'

    name = Column(String(50), primary_key=True)
    value = Column(String(160))

    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value
    
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            field = getattr(self, column.name)
            if field is None:
                d[column.name] = field
            elif str(field) in ['True', 'False', 'true', 'false']:
                d[column.name] = bool(field)
            else:
                d[column.name] = str(field)