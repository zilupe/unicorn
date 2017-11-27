from cached_property import cached_property
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

session_factory = sessionmaker()
Session = scoped_session(session_factory)
metadata = MetaData()


class _Base:
    default_order_by = None
    id = None

    @classmethod
    def get_all(cls, order_by=None):
        q = Session.query(cls)
        if order_by is not None:
            q = q.order_by(*order_by)
        elif cls.default_order_by is not None:
            q = q.order_by(*cls.default_order_by)
        return q

    @classmethod
    def get_by_id(cls, id):
        return Session.query(cls).filter(cls.id == id).one()

    @classmethod
    def get_count(cls):
        return Session.query(cls).count()

    @classmethod
    def create(cls, **kwargs):
        inst = cls(**kwargs)
        Session.add(inst)
        Session.commit()
        return inst

    @cached_property
    def type_name(self):
        return self.__class__.__tablename__[:-1]

    @cached_property
    def simple_url(self):
        return '{}_{}.html'.format(self.type_name, self.id)

    @cached_property
    def simple_link(self):
        return '<a href="{}">{}</a>'.format(self.simple_url, self.simple_label)

    @cached_property
    def simple_label(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return '{} {}'.format(self.type_name, self.id)

    def __repr__(self):
        return '<{} id={} {!r}>'.format(self.__class__.__name__, self.id, self.simple_label)


Base = declarative_base(metadata=metadata, cls=_Base)
