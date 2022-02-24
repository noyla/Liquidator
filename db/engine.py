from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# create an engine
# engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')

# create a configured "Session" class
# Session = sessionmaker(bind=engine)

# create a Session
# session = Session()

Base = declarative_base()