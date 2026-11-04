# MySQL

MySQL is an open-source relational database management system (RDBMS) and one of the most widely deployed databases in the world, especially in web application stacks (LAMP). It uses [SQL](sql.md) and is known for being fast, easy to set up, and well-supported by hosting providers. MariaDB is a community fork of MySQL that maintains drop-in compatibility.

## When to Use MySQL

| Good fit | Poor fit |
|---|---|
| Web apps (WordPress, Laravel, [Django](../../programming/python/django.md)) | Complex queries with CTEs / window functions (prefer [PostgreSQL](postgresql.md)) |
| Read-heavy workloads | Full [JSON](../../programming/fundamentals/json.md) / array column needs |
| Teams already on LAMP/LEMP stack | Strict standards compliance |
| Managed cloud (RDS, Cloud [SQL](sql.md), PlanetScale) | Advanced replication / logical decoding |

## Installation

```bash
# Ubuntu / Debian
sudo apt install mysql-server -y
sudo systemctl enable --now mysql
sudo mysql_secure_installation

# Docker (quickest)
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=myuser \
  -e MYSQL_PASSWORD=mypass \
  -p 3306:3306 \
  mysql:8.0
```

## Docker Compose

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: mydb
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro

volumes:
  mysql_data:
```

## MySQL CLI

```bash
# Connect
mysql -u myuser -p mydb

# Inside mysql shell
SHOW DATABASES;
USE mydb;
SHOW TABLES;
DESCRIBE users;
EXIT;

# Run a SQL file
mysql -u myuser -p mydb < schema.sql

# Dump a database
mysqldump -u myuser -p mydb > backup.sql

# Restore
mysql -u myuser -p mydb < backup.sql
```

## Core SQL (MySQL Syntax)

```sql
-- Create table
CREATE TABLE users (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    role       ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Query
SELECT * FROM users WHERE role = 'admin' ORDER BY created_at DESC LIMIT 10;

-- Update
UPDATE users SET role = 'admin' WHERE id = 1;

-- Delete
DELETE FROM users WHERE id = 1;

-- Add index
CREATE INDEX idx_users_email ON users(email);

-- Full-text index
ALTER TABLE posts ADD FULLTEXT(title, body);
SELECT * FROM posts WHERE MATCH(title, body) AGAINST('search term' IN NATURAL LANGUAGE MODE);
```

## Python Client (`mysql-connector-python`)

```bash
pip install mysql-connector-python python-dotenv
```

```python
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    database=os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
)

cursor = conn.cursor(dictionary=True)   # returns rows as dicts

cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
user = cursor.fetchone()
print(user)

cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("Bob", "bob@example.com"))
conn.commit()

cursor.close()
conn.close()
```

Use **`%s`** as the placeholder (not `?` like [SQLite](sqlite.md)).

## SQLAlchemy with MySQL

```bash
pip install sqlalchemy pymysql
```

```python
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', 3306)}"
    f"/{os.getenv('MYSQL_DATABASE')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
```

`pool_pre_ping=True` prevents stale connection errors after the server closes idle connections.

## Environment Variables

```bash
# .env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=mydb
MYSQL_USER=myuser
MYSQL_PASSWORD=secret
```

## Storage Engines

| Engine | Use case |
|---|---|
| **InnoDB** (default) | [ACID](acid.md) transactions, foreign keys — use for everything |
| **MyISAM** (legacy) | Read-heavy, no transactions — avoid in new projects |
| **MEMORY** | In-memory temp tables — lost on restart |

Always use **InnoDB**. MyISAM does not support transactions or foreign keys.

## JSON Support

```sql
CREATE TABLE events (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    data JSON
);

INSERT INTO events (data) VALUES ('{"type": "login", "user_id": 42}');

-- Query JSON field
SELECT data->>'$.user_id' AS user_id FROM events WHERE data->>'$.type' = 'login';

-- Index a JSON path
ALTER TABLE events ADD COLUMN user_id INT GENERATED ALWAYS AS (data->>'$.user_id') STORED;
CREATE INDEX idx_user_id ON events(user_id);
```

## User Management

```sql
-- Create a user
CREATE USER 'appuser'@'%' IDENTIFIED BY 'strongpassword';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'appuser'@'%';
FLUSH PRIVILEGES;

-- Revoke
REVOKE DELETE ON mydb.* FROM 'appuser'@'%';

-- Show grants
SHOW GRANTS FOR 'appuser'@'%';

-- Drop user
DROP USER 'appuser'@'%';
```

## Replication (Primary–Replica)

MySQL supports primary–replica replication for read scaling and high availability:

1. Enable binary logging on primary (`log_bin=ON`)
2. Create a replication user on primary
3. Configure replica with `CHANGE MASTER TO ...`
4. Start replica with `START REPLICA`

For production HA, use **MySQL Group Replication** or a managed service ([AWS](../../cloud/infrastructure/aws.md) RDS Multi-AZ, PlanetScale, Cloud [SQL](sql.md)).

## MySQL vs PostgreSQL vs SQLite

| | MySQL | [PostgreSQL](postgresql.md) | [SQLite](sqlite.md) |
|---|---|---|---|
| Server | Required | Required | None (embedded) |
| [JSON](../../programming/fundamentals/json.md) | Basic | Rich (JSONB, operators) | None |
| Window functions | Yes (8.0+) | Yes (full) | Yes (3.25+) |
| Full-text search | FULLTEXT index | `tsvector` / `pg_trgm` | FTS5 |
| Standards compliance | Moderate | High | Moderate |
| Ecosystem | WordPress, Laravel, Rails | [Django](../../programming/python/django.md), [FastAPI](../../programming/python/fastapi.md), data tools | Mobile, embedded, CLI |
| Best for | Web apps, broad hosting support | Complex queries, data integrity | Local / embedded |

## Related Concepts

- [systemctl (systemd) Commands](../../../commands/systemctl.md) — managing the `mysql` service itself (start/stop/restart/logs) beyond the initial `enable --now`
- [PostgreSQL](./postgresql.md) — more feature-rich alternative
- [SQLite](./sqlite.md) — embedded, no-server alternative for dev/local use
- [SQL](./sql.md) — [SQL](sql.md) fundamentals
- [ACID](./acid.md) — MySQL InnoDB is fully [ACID](acid.md)-compliant
- [ORM](../../backend/data/orm.md) — SQLAlchemy, [Django](../../programming/python/django.md) [ORM](../../backend/data/orm.md) with MySQL
