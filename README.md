# Flaxon PostSQL

`flaxon-postsql` is a lightweight PostgreSQL wrapper built on `asyncpg`. It
owns an async connection pool and exposes it as `app.state.postsql`.

## Install

```bash
git clone https://github.com/aldanedev-create/flaxon-postsql.git
cd flaxon-postsql
pip install .
```

PyPI publishing is not configured yet; install from the repository until a
release is published.

## Use

```python
import os

from flaxon import Flaxon
from flaxon_postsql import PostSQLPlugin

app = Flaxon("catalog")
await app.plugins.load_plugin(PostSQLPlugin(os.environ["DATABASE_URL"], min_size=2, max_size=10))


@app.get("/products")
async def list_products():
    rows = await app.state.postsql.fetch("SELECT id, name FROM products ORDER BY id")
    return {"products": [dict(row) for row in rows]}
```

The connection pool opens during application startup and closes during
shutdown. Always use positional `$1`, `$2`, … parameters with `asyncpg`; do
not build SQL with string interpolation. Store the database URL in a secret
manager or environment variable.

This project is named `postsql` at the package level but integrates with
PostgreSQL through `asyncpg`.
