if __name__ == "__main__":
    import sys,os
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(path)
    sys.path.append(os.path.dirname(path))
    sys.path.append(path)
    sys.path.append(os.path.join(path, "FUNCS"))

from zxutil.FUNCS.sql import SqlAlchemyWrapper
import sqlalchemy
import logging
from sqlalchemy.orm import Session as S
import os 

package_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print(package_path)

sql = SqlAlchemyWrapper(
    path=f"{package_path}/bookrags_record.db",
)

class BookragsRecord(sql.base):
    __tablename__ = "records"
    link = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    book_name = sqlalchemy.Column(sqlalchemy.String)
    fetched_from = sqlalchemy.Column(sqlalchemy.String)

    @classmethod
    @sql.session()
    def get_all(cls, session : S= None):
        return session.query(cls).all()

    @classmethod
    @sql.session()
    def insert(cls, link : str, book_name : str,fetched_from: str, session :S= None):
        try:
            record = BookragsRecord(link=link, book_name=book_name, fetched_from=fetched_from)
            session.add(record)
            session.commit()
            return True
        except:
            session.rollback()
            logging.error(f"error inserting {book_name}")
            return False


if __name__ == "__main__":
    sql.engine.echo = True
    print(BookragsRecord.get_all()[0].book_name)