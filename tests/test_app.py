def test_has_db_name(app, two_seasons):
    assert app.db_name.startswith('test_unicorn_')
    pass
