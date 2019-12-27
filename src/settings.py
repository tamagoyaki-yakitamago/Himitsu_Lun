from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# データベース接続情報
DATABASE = "postgresql"
USER = "postgres"
PASSWORD = "postgres"
HOST = "db"
PORT = "543２"
DB_NAME = "himitsu_lun_db"

CONNECT_STR = "{}://{}:{}@{}:{}/{}".format(
    DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME
)

ENGINE = create_engine(CONNECT_STR, echo=True)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=ENGINE))

Base = declarative_base()
