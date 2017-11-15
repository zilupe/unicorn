from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


session_factory = sessionmaker()
Session = scoped_session(session_factory)
metadata = MetaData()


class _Base:
    @classmethod
    def get_all(cls):
        return Session.query(cls)

    @classmethod
    def create(cls, **kwargs):
        inst = cls(**kwargs)
        Session.add(inst)
        Session.commit()
        return inst


Base = declarative_base(metadata=metadata, cls=_Base)
