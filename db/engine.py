import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy_utils import database_exists

# create an engine
# engine = create_engine('mysql+pymysql://root:password1@127.0.0.1:3306/liquidator')
engine = create_engine(os.environ.get('JAWSDB_MARIA_URL'))
# engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')
Base = declarative_base(engine)

def create_database():
    with engine.connect() as conn:
        conn.execute("CREATE DATABASE IF NOT EXISTS liquidator CHARACTER SET=utf8mb4")

    # if not database_exists(engine.url):
        # create_database(engine.url)

def create_tables():
    Base.metadata.create_all(engine)



# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()