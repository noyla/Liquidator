import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy_utils import database_exists

# create an engine
from dotenv import load_dotenv
load_dotenv() # load environment variables from .env.
engine = create_engine('mysql+pymysql://root:password1@127.0.0.1:3306/liquidator')

# db_url = os.environ.get('JAWSDB_MARIA_URL')
# if not db_url:
    # exit()
# engine = create_engine(db_url)
# engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')

Base = declarative_base(engine)

def create_database():
    with engine.connect() as conn:
        conn.execute("CREATE DATABASE IF NOT EXISTS liquidator CHARACTER SET=utf8mb4")

    # if not database_exists(engine.url):
        # create_database(engine.url)

def create_tables():
    Base.metadata.create_all(engine)

def execute_statement(stmt: str, params: dict = None):
    with engine.connect() as conn:
        conn.execute(stmt)
        # conn.execute(stmt, params)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()


if __name__ == '__main__':
    print("Executing")
    sql_add_users_create_at = "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
    sql_add_users_reserve_data_create_at = "ALTER TABLE users_reserve_data ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
    # sql = "UPDATE"
    execute_statement(sql_add_users_reserve_data_create_at)