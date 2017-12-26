"""
RuntimeContext.
Thread-safe.
"""

import contextlib
import os
import threading

from cached_property import cached_property
from sqlalchemy import create_engine


_thread_local = threading.local()
_thread_local.stack = []


class RuntimeContext:
    _allowed_vars = (
        'dry_run',
    )

    def __init__(self):
        self._stack = _thread_local.stack

    def __getattr__(self, name):
        if name in self._allowed_vars:
            return self.get(name)
        raise AttributeError(name)

    def get(self, name, default=None):
        if name not in self._allowed_vars:
            raise AttributeError(name)
        for ctx in reversed(self._stack):
            if name in ctx:
                return ctx[name]
        return default

    def __call__(self, **kwargs):
        @contextlib.contextmanager
        def ctx_manager():
            self._stack.append(kwargs)
            try:
                yield self
            finally:
                self._stack.pop()
        return ctx_manager()


class App(RuntimeContext):
    _allowed_vars = (
        'dry_run',
        'db_name',
    )

    @property
    def db_url(self):
        # Do not cache this result as user may modify the URL (for example, in tests).
        return (
            'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{name}'
        ).format(
            user=os.environ.get('UNICORN_DB_USER', 'root'),
            host=os.environ.get('UNICORN_DB_HOST', 'localhost'),
            password=os.environ.get('UNICORN_DB_PASSWORD', ''),
            port=os.environ.get('UNICORN_DB_PORT', 3306),
            name=os.environ.get('UNICORN_DB_NAME', 'unicorn'),
        )

    @cached_property
    def db_engine(self):
        return create_engine(self.db_url)


app = App()
