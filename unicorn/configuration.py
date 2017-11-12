import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


log = logging.getLogger(__name__)


db_engine = create_engine('sqlite://')

Session = sessionmaker(db_engine)
Session.configure(bind=db_engine)


_main_session = None


def get_session():
    global _main_session
    if _main_session is None:
        _main_session = Session()
    return _main_session
