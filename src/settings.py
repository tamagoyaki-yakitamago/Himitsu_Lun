import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# データベース接続情報
# 環境変数から呼び出し
DATABASE = os.environ.get("DB_DATABASE")
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("DB_HOST")
PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

CONNECT_STR = "{}://{}:{}@{}:{}/{}".format(
    DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME
)

ENGINE = create_engine(CONNECT_STR, echo=True)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=ENGINE))

Base = declarative_base()
