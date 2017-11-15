from unicorn.core.apps import App


class UnicornApp(App):
    pass


def create_app(**kwargs):
    app = UnicornApp(**kwargs)

    # TODO Make this cleaner later
    import unicorn.db.connection

    return app


def run_in_app_context(func):
    with create_app():
        func()
