# SQLite

SQLite is a self-contained, serverless, zero-configuration [SQL](sql.md) database engine. The entire database is stored in a single file on disk. There is no separate server process — the library is linked directly into the application, and all reads/writes go through the file system. It is the most widely deployed database engine in the world (browsers, mobile apps, desktop tools, embedded systems).

## When to Use SQLite

| Good fit | Poor fit |
|---|---|
| Local / embedded apps | High-concurrency multi-writer apps |
| CLI tools and scripts | Applications that need user/role management |
| Prototyping and dev | Data too large for one file |
| Test databases (fast, no setup) | Distributed or replicated setups |
| Mobile apps (iOS/Android) | Full-text or vector search at scale |
| Read-heavy, low-write apps | |

**One writer at a time** — SQLite uses file-level locking. For multi-writer server applications, use [PostgreSQL](postgresql.md) or [MySQL](mysql.md).

## File Structure

```
myapp.db    ← entire database in one file (tables, indexes, data, schema)
myapp.db-wal   ← write-ahead log (present during active writes)
myapp.db-shm   ← shared memory file (WAL mode only)
```

## Python (Built-in `sqlite3`)

No installation needed — `sqlite3` is in the Python standard library.

```python
import sqlite3

# Connect (creates file if it doesn't exist)
conn = sqlite3.connect("myapp.db")

# In-memory database (no file, lost on close — great for tests)
conn = sqlite3.connect(":memory:")

# Return rows as dicts
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL,
        email TEXT    UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Insert
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
conn.commit()

# Query
cursor.execute("SELECT * FROM users WHERE name = ?", ("Alice",))
rows = cursor.fetchall()
for row in rows:
    print(dict(row))

# Update
cursor.execute("UPDATE users SET name = ? WHERE id = ?", ("Alicia", 1))
conn.commit()

# Delete
cursor.execute("DELETE FROM users WHERE id = ?", (1,))
conn.commit()

conn.close()
```

### Context manager (auto-commit / rollback)

```python
with sqlite3.connect("myapp.db") as conn:
    conn.row_factory = sqlite3.Row
    conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))
    # commits on exit, rolls back on exception
```

## SQLAlchemy ORM with SQLite

```bash
pip install sqlalchemy
```

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime, timezone

engine = create_engine("sqlite:///myapp.db")          # file
# engine = create_engine("sqlite:///:memory:")        # in-memory

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()

    users = session.query(User).filter(User.name == "Alice").all()
```

## FastAPI + SQLite (dev setup)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`check_same_thread=False` is required for [FastAPI](../../programming/python/fastapi.md) because requests may be handled across threads.

## Useful Pragmas

```sql
-- Enable WAL mode (better concurrency for reads during writes)
PRAGMA journal_mode=WAL;

-- Enable foreign key enforcement (OFF by default!)
PRAGMA foreign_keys=ON;

-- Set cache size (pages, negative = KiB)
PRAGMA cache_size=-64000;   -- 64 MB

-- Check database integrity
PRAGMA integrity_check;
```

Always enable `foreign_keys=ON` — it is **disabled by default** in SQLite.

## CLI

```bash
# Open a database
sqlite3 myapp.db

# Inside sqlite3 shell
.tables                     -- list tables
.schema users               -- show CREATE statement
.mode column                -- column-aligned output
.headers on
SELECT * FROM users LIMIT 5;
.quit
```

## Data Types

SQLite uses **dynamic typing** — the type affinity system is more flexible than strict [SQL](sql.md):

| Affinity | Storage classes |
|---|---|
| `INTEGER` | 1, 2, 3, 4, 6, or 8 byte signed int |
| `REAL` | 8-byte IEEE float |
| `TEXT` | UTF-8 / UTF-16 string |
| `BLOB` | Raw bytes |
| `NUMERIC` | Integer or real depending on value |

You can store any value in any column — SQLite will convert if possible.

## SQLite vs PostgreSQL vs MySQL

| | SQLite | [PostgreSQL](postgresql.md) | [MySQL](mysql.md) |
|---|---|---|---|
| Server | None (embedded) | Required | Required |
| Concurrency | One writer | Many concurrent writers | Many concurrent writers |
| Data types | Flexible (dynamic) | Strict, rich ([JSON](../../programming/fundamentals/json.md), arrays, [UUID](uuid.md)) | Strict |
| Max DB size | ~281 TB (practical: a few GB) | Unlimited | Unlimited |
| Full-text search | Basic FTS5 | `tsvector` / `pg_trgm` | FULLTEXT index |
| Best for | Local / embedded / tests | Production web apps | Web apps, WordPress ecosystem |

## Related Concepts

- [PostgreSQL](./postgresql.md) — production-grade relational database
- [MySQL](./mysql.md) — alternative production relational database
- [SQL](./sql.md) — [SQL](sql.md) fundamentals
- [ORM](../../backend/data/orm.md) — SQLAlchemy and other ORMs
- [ACID](./acid.md) — SQLite is fully [ACID](acid.md)-compliant
