import os

from sqlalchemy import create_engine

from .base import Session

engine = create_engine(os.environ.get('UNICORN_DATABASE_URL', 'mysql+mysqlconnector://root@localhost:3306/unicorn'))
Session.configure(bind=engine)
