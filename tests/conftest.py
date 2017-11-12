import pytest

from unicorn.configuration import Session, db_engine
from unicorn.models import Base


@pytest.fixture(scope='session')
def db():
    Base.metadata.create_all(db_engine)
