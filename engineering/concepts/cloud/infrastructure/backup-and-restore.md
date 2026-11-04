# Backup and Restore

## What is it?

Backup is the process of creating a copy of important data so it can be recovered if the original is lost, corrupted, or accidentally deleted. Restore is the process of recovering from that copy. Together, backup and restore form the safety net that makes a system production-worthy.

## The Critical Distinction: Docker Image ≠ Backup

A [Docker](../../containers/docker.md) image contains application software — not your data:

```
Docker Image (nextcloud:27) contains:
  ├── PHP runtime
  ├── Apache web server
  ├── Nextcloud application code
  └── System libraries

Docker Image does NOT contain:
  ├── User uploaded files          ← lives in nextcloud_data volume
  ├── Database (users, metadata)   ← lives in db_data volume
  └── Nextcloud configuration      ← lives in nextcloud_data volume
```

**If you run `docker compose down -v` and think "I can just pull the image again," you have lost all your data permanently.** The image is re-downloadable. The data is not.

## What Must Be Backed Up

| Data | Location | Backup method |
|---|---|---|
| Nextcloud files | [Docker](../../containers/docker.md) volume `nextcloud_data` → `/var/www/html/data/` | `tar` + `gzip` |
| Nextcloud config | [Docker](../../containers/docker.md) volume `nextcloud_data` → `/var/www/html/config/` | included in above |
| Database | [Docker](../../containers/docker.md) volume `db_data` | `pg_dump` ([PostgreSQL](../../databases/relational/postgresql.md)) or `mysqldump` (MariaDB) |
| `.env` file | VM filesystem | Copy to secure location |
| `docker-compose.yml` | Repo (already in Git) | Git is the backup |

## The Backup Process

```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nextcloud_backup_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..."

# Step 1: Enable Nextcloud maintenance mode (prevents data changes during backup)
docker exec nextcloud php occ maintenance:mode --on

# Step 2: Back up Nextcloud files
docker run --rm \
  --volumes-from nextcloud \
  -v "$BACKUP_DIR":/backup \
  ubuntu \
  tar czf /backup/nextcloud_data_$DATE.tar.gz /var/www/html

# Step 3: Back up database
docker exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/db_$DATE.sql"

# Step 4: Disable maintenance mode
docker exec nextcloud php occ maintenance:mode --off

# Step 5: Copy .env file
cp /opt/nextcloud/.env "$BACKUP_DIR/env_$DATE.bak"

echo "[$(date)] Backup complete: $BACKUP_DIR"
```

## The Restore Process

```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/backups"
# Set these to the specific backup files to restore from:
NEXTCLOUD_BACKUP="$BACKUP_DIR/nextcloud_data_20260920_120000.tar.gz"
DB_BACKUP="$BACKUP_DIR/db_20260920_120000.sql"

echo "[$(date)] Starting restore..."

# Step 1: Stop the stack
docker compose down

# Step 2: Restore Nextcloud files
docker run --rm \
  --volumes-from nextcloud \
  -v "$BACKUP_DIR":/backup \
  ubuntu \
  bash -c "cd / && tar xzf /backup/$(basename $NEXTCLOUD_BACKUP)"

# Step 3: Restore database
docker compose up -d db
sleep 5  # wait for DB to start
docker exec -i db psql -U "$POSTGRES_USER" "$POSTGRES_DB" < "$DB_BACKUP"

# Step 4: Start everything
docker compose up -d

echo "[$(date)] Restore complete."
```

## Backup Strategy

| Aspect | Decision |
|---|---|
| **What is backed up** | Nextcloud files + config, database, `.env` |
| **Where backups are stored** | `/opt/backups/` on the VM (for demo); ideally [Azure Blob Storage](../azure/azure-blob-storage.md) for production |
| **Frequency** | Manual for demo; daily cron job recommended for production |
| **Retention** | Keep last 7 daily backups (delete older ones to save space) |
| **Protection** | Backup location should be separate from the application (separate disk or cloud storage) |
| **Verification** | Run a restore test after every backup to confirm the backup is valid |

## Restore Testing

A backup that has never been tested is not a backup — it is an assumption.

The restore test process:
1. Take a backup with `./backup.sh`
2. **In a test environment** (not the live system): run `docker compose down -v` to simulate data loss
3. Run `./restore.sh` using the backup created in step 1
4. Verify: log in to Nextcloud, check files are there, check users exist
5. Document the result

## How it Fits in This Project

Backup and restore is owned by Member 3 (IT) and reviewed by Member 2 (Cybersecurity). The scripts are `deployment/scripts/backup.sh` and `deployment/scripts/restore.sh`. The procedure is documented in `docs/backup-restore.md`. The final demo includes a live demonstration of running `./backup.sh` successfully. The data being protected lives on the [virtual machine](virtual-machines.md) provisioned via [Terraform](terraform.md).

## Related

- [Virtual Machines](virtual-machines.md)
- [Microsoft Azure](azure.md)
- [Object Storage](object-storage.md)
- [Docker Compose](../../containers/docker-compose.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
