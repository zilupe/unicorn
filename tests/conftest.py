import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope='session')
def db():
    from unicorn.db.base import Base, Session
    engine = create_engine('sqlite:///')
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
