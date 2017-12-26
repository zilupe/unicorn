from unicorn.runtime_context import RuntimeContext


def test_runtime_context():
    context = RuntimeContext()

    assert context.dry_run is None
    with context(dry_run=True):
        assert context.dry_run is True
        with context(dry_run=False):
            assert context.dry_run is False
        assert context.dry_run is True
    assert context.dry_run is None

