def test_has_db_name(app):
    assert app.db_name.startswith('test_unicorn_')
