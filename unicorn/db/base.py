from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


session_factory = sessionmaker()
Session = scoped_session(session_factory)
metadata = MetaData()


class _Base:
    default_order_by = None

    @classmethod
    def get_all(cls, order_by=None):
        q = Session.query(cls)
        if order_by:
            q = q.order_by(*order_by)
        elif cls.default_order_by:
            q = q.order_by(*cls.default_order_by)
        return q

    @classmethod
    def get_count(cls):
        return Session.query(cls).count()

    @classmethod
    def create(cls, **kwargs):
        inst = cls(**kwargs)
        Session.add(inst)
        Session.commit()
        return inst


Base = declarative_base(metadata=metadata, cls=_Base)
