from __future__ import with_statement
import os.path
import sys

from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from unicorn.models import metadata
from unicorn.app import app

config = context.config

target_metadata = metadata


def run_migrations_offline():
    context.configure(url=app.get_db_url(), target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with app.db_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
