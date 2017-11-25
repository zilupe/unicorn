import pytest
from sqlalchemy import create_engine

from unicorn.app import create_app
from unicorn.models import Season


@pytest.fixture(scope='session')
def app_context():
    app_context = create_app().app_context()
    app_context.push()
    yield app_context
    app_context.pop()


@pytest.fixture(scope='session')
def db():
    from unicorn.db.base import Base, Session
    engine = create_engine('sqlite:///')
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
