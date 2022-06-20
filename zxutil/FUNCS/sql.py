import os
import shutil
from sqlalchemy import create_engine
import sqlalchemy
import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session as S
import functools
from sqlalchemy.ext.declarative import declarative_base

class SqlAlchemyWrapper:
    def __init__(
        self, 
        path : str, 
        type="sqlite", 
        echo=False
    ):
        self._path = path
        self._pre_init(path)
        self.engine = create_engine(f"{type}:///{path}", echo=echo)
        self.base = declarative_base()
     

    def _pre_init(self, path):
        if os.path.exists(path):
            return
        
        conn = sqlite3.connect(path)
        conn.close()

    def create_all(self):
        self.base.metadata.create_all(self.engine)

    def session(self):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                session = kwargs.get("session", None)
                session_has = session is not None
                if session is None:
                    Session = sessionmaker(bind=self.engine)
                    session : S = Session()
                    kwargs["session"] = session
                
                val = func(*args, **kwargs)
                if not session_has:
                    session.close()
                return val
            return wrapper
        return decorator


    def make_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def copy_db(self, path):
        shutil.copy(self._path, path)


        