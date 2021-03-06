import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# データベース接続情報
with open("secure/authentication.txt", "r") as f:
    DATABASE = f.readline()
    DATABASE = DATABASE.rstrip(os.linesep)
    USER = f.readline()
    USER = USER.rstrip(os.linesep)
    PASSWORD = f.readline()
    PASSWORD = PASSWORD.rstrip(os.linesep)
    HOST = f.readline()
    HOST = HOST.rstrip(os.linesep)
    PORT = f.readline()
    PORT = PORT.rstrip(os.linesep)
    DB_NAME = f.readline()
    DB_NAME = DB_NAME.rstrip(os.linesep)
# 環境変数から呼び出し
"""
DATABASE = os.environ.get("DB_DATABASE")
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("DB_HOST")
PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
"""

CONNECT_STR = "{}://{}:{}@{}:{}/{}".format(
    DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME
)

ENGINE = create_engine(CONNECT_STR, echo=True)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=ENGINE))

Base = declarative_base()
