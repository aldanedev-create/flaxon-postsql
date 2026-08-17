"""PostgreSQL connection-pool integration."""

from __future__ import annotations

from typing import Any

from flaxon.plugins import Plugin


class PostSQLDatabase:
    """Own an asyncpg connection pool for one PostgreSQL database."""

    def __init__(self, dsn: str, pool_options: dict[str, Any] | None = None) -> None:
        if not dsn:
            raise ValueError("A non-empty PostgreSQL DSN is required")
        self.dsn = dsn
        self.pool_options = dict(pool_options or {})
        self.pool: Any = None

    async def connect(self) -> None:
        """Create the connection pool once at application startup."""
        if self.pool is not None:
            return
        try:
            import asyncpg
        except ImportError as exc:  # pragma: no cover - dependency metadata covers this
            raise RuntimeError("Install asyncpg before starting the application") from exc
        self.pool = await asyncpg.create_pool(self.dsn, **self.pool_options)

    async def close(self) -> None:
        """Close all connections at application shutdown."""
        if self.pool is not None:
            await self.pool.close()
        self.pool = None

    def _require_pool(self) -> Any:
        if self.pool is None:
            raise RuntimeError("PostSQL is not connected; wait for application startup")
        return self.pool

    async def execute(self, query: str, *args: Any) -> str:
        """Execute a statement and return asyncpg's status string."""
        return await self._require_pool().execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[Any]:
        """Run a query and return all records."""
        return await self._require_pool().fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Any:
        """Run a query and return one record, or ``None``."""
        return await self._require_pool().fetchrow(query, *args)


class PostSQLPlugin(Plugin):
    """Expose :class:`PostSQLDatabase` through ``app.state.postsql``."""

    name = "flaxon-postsql"
    version = "0.1.0"
    description = "Async PostgreSQL connection-pool lifecycle for Flaxon"
    provides = ["postgresql"]

    def __init__(self, dsn: str, **pool_options: Any) -> None:
        self.database = PostSQLDatabase(dsn, pool_options)

    def setup(self, app: Any) -> None:
        app.state.postsql = self.database
        app.lifecycle.on_startup(self.database.connect)
        app.lifecycle.on_shutdown(self.database.close)
