import datetime as dt
import os.path

import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope='session')
def unicorn_db_name():
    return 'test_unicorn_{}'.format(dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S'))


@pytest.fixture(scope='session')
def app(unicorn_db_name):
    from unicorn.app import app
    with app(db_name=unicorn_db_name):
        yield app


@pytest.fixture(scope='session')
def db(app):
    setup_engine = create_engine(app.get_db_url(db_name=''))

    setup_engine.execute((
        'CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
    ).format(app.db_name))

    from unicorn.models import metadata
    metadata.bind = app.db_engine

    metadata.create_all()

    try:
        yield app.db_engine
    finally:
        app.db_session.remove()
        setup_engine.execute('DROP DATABASE {}'.format(app.db_name))


@pytest.fixture(scope='session')
def two_seasons(db):
    from unicorn.v2.go import process_season, source_dir
    process_season(os.path.join(source_dir, '2014-Autumn.htm'))
    process_season(os.path.join(source_dir, '2015-Winter.htm'))
