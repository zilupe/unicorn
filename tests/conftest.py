import datetime as dt

import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope='session')
def unicorn_db_name():
    return 'test_unicorn_{}'.format(dt.datetime.utcnow().isoformat())


@pytest.fixture(scope='session')
def app(unicorn_db_name):
    from unicorn.runtime_context import app
    app.db_name = unicorn_db_name
    yield app


@pytest.fixture(scope='session')
def db(app):
    db_url = app.create_db_url()
    db_url.database = None
    setup_engine = create_engine(db_url)
    test_engine = create_engine(app.db_url)

    setup_engine.execute((
        'CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
    ).format(app.db_name))

    yield test_engine

    setup_engine.execute((
        'DROP DATABASE {}'
    ).format(app.db_name))
