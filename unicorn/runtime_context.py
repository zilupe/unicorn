"""
RuntimeContext.
Thread-safe.
"""

import contextlib
import threading

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

    def set(self, name, value):
        if name not in self._allowed_vars:
            raise AttributeError(name)
        if not self._stack:
            raise RuntimeError('Trying to set context variable {!r} outside of runtime context'.format(name))
        self._stack[-1][name] = value

    def __contains__(self, name):
        return any(name in ctx for ctx in reversed(self._stack))

    def __call__(self, **kwargs):
        @contextlib.contextmanager
        def ctx_manager():
            self._stack.append(kwargs)
            try:
                yield self
            finally:
                self._stack.pop()
        return ctx_manager()
