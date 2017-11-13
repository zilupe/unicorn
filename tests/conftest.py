import pytest

from unicorn.db import Base, engine


@pytest.fixture(scope='session')
def db():
    Base.metadata.create_all(engine)
