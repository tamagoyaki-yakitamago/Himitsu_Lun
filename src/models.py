import sys

from sqlalchemy import Column, Integer, String, DateTime, Sequence
from settings import ENGINE, Base
from datetime import datetime


class Himitsu_lun(Base):
    # テーブル"himitsu_lun_table"
    __tablename__ = "himitsu_lun_table"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    share_id = Column(Integer, nullable=False)
    share = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    delete_at = Column(DateTime, default=datetime.now, nullable=False)


def main(args):
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main(sys.argv)
