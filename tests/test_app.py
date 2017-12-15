from unicorn.core.apps import current_app


def test_current_season(app_context):
    assert current_app.current_season
