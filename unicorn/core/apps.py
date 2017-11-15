"""
If you know Flask then you will understand this.

This depends on LocalStack and LocalProxy which you can find in werkzeug.local

In order to manage global state, we introduce a few concepts:

- Application (app)
- Application context (app_context)
- Current application (current_app)

An application object represents the core of your application which is in control of everything.
Normally you have just one application instance and it has your application configuration associated
with it.

Application context is a context that is associate with one application and is used by
that app to answer queries. Application contexts can be stacked upon each other. The top-most
context is used to determine what is the current application instance in charge.

Current application is a proxy to the current application instance in charge.

There is a global stack of application contexts and there is also a local stack of contexts stored
by each application instance so they know which context to ask details from.

    app = create_app()
    with app.app_context(client_prefix='ford'):

        # somewhere deep in your application where you don't have
        # access to the app, you can import current_app and do:
        assert current_app.client_prefix == 'ford'

        # you can also go deeper:
        with current_app.app_context(client_prefix='nike'):
            assert current_app.client_prefix == 'nike'

        # once you exit the context, you are back to where you before:
        assert current_app.client_prefix == 'ford'

An instance of app can also be used as a context manager in which case a context with context defaults
(passed on app creation) will be created:

    app = create_app(client_prefix='ford')

    with app:
        assert current_app.client_prefix == 'ford'

"""

from werkzeug.local import LocalStack, LocalProxy

_app_context_stack = LocalStack()


def _get_current_app():
    if _app_context_stack.top:
        return _app_context_stack.top.app
    else:
        raise RuntimeError('Working outside of app context')


current_app = LocalProxy(_get_current_app)


class AppContext:
    def __init__(self, app, **context):
        self.app = app
        self.__dict__.update(context)

    def __enter__(self):
        self.push()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()

    def push(self):
        self.app.push_context(self)

    def pop(self):
        self.app.pop_context(self)


class App:
    context_cls = AppContext

    def __init__(self, **context_defaults):
        self._context_stack = []
        self._context_defaults = context_defaults

    def app_context(self, **context):
        for k, v in self._context_defaults.items():
            context.setdefault(k, v)
        return self.context_cls(app=self, **context)

    def push_context(self, context):
        assert context.app is self
        self._context_stack.append(context)
        _app_context_stack.push(context)

    def pop_context(self, context=None):
        if context is not None and _app_context_stack.top != context:
            raise RuntimeError('Cannot pop the context - it is not the current application context')
        if _app_context_stack.top != self._context_stack[-1]:
            raise RuntimeError('Cannot pop the context - this app is not in charge of the current application context')
        _app_context_stack.pop()
        self._context_stack.pop()

    def __getattribute__(self, name):
        # If you have added an attribute to your custom context class and get an AttributeError here,
        # it is because you haven't registered the attribute on your App class.
        value = object.__getattribute__(self, name)

        if name.startswith('_'):
            return value

        for ctx in reversed(self._context_stack):
            try:
                value = getattr(ctx, name)
                break
            except AttributeError:
                continue

        return value

    def __enter__(self):
        self.app_context().push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop_context()
