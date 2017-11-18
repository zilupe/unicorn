import unicorn.db.connection
import unicorn.models
from unicorn.app import run_in_app_context
from unicorn.configuration import logging
from unicorn.db.base import Base

log = logging.getLogger(__name__)


@run_in_app_context
def main():
    log.info('Dropping and recreating database')
    with unicorn.db.connection.engine.begin() as db_conn:
        db_conn.execute('DROP DATABASE unicorn')
        db_conn.execute('CREATE DATABASE unicorn')

    # This doesn't work with constraints:
    # log.info('Dropping all tables')
    # Base.metadata.drop_all(unicorn.db.connection.engine)

    log.info('Creating all tables')
    with unicorn.db.connection.engine.begin():
        Base.metadata.create_all(unicorn.db.connection.engine)


if __name__ == '__main__':
    main()
