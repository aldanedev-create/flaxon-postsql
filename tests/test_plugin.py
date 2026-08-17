import pytest

from flaxon import Flaxon
from flaxon_postsql import PostSQLPlugin


def test_plugin_registers_database_and_lifecycle_handlers() -> None:
    app = Flaxon("test")
    plugin = PostSQLPlugin("postgresql://localhost/example", min_size=2, max_size=8)

    plugin.setup(app)

    assert app.state.postsql is plugin.database
    assert plugin.database.pool_options == {"min_size": 2, "max_size": 8}
    assert app.lifecycle.startup_count == 1
    assert app.lifecycle.shutdown_count == 1


@pytest.mark.asyncio
async def test_queries_fail_before_startup() -> None:
    plugin = PostSQLPlugin("postgresql://localhost/example")

    with pytest.raises(RuntimeError, match="not connected"):
        await plugin.database.fetch("SELECT 1")
