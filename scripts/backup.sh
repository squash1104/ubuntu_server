#!/usr/bin/env bash
set -euo pipefail

# Simple on-server backup for SisVot (code + Postgres dump)
# - Code archive: /srv/backups/code/sisvot_code_YYYYmmdd_HHMMSS.tar.gz
# - DB dump:      /srv/backups/db/sisvot_db_YYYYmmdd_HHMMSS.sql.gz

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_ROOT="/srv/backups"
CODE_DIR="${BACKUP_ROOT}/code"
DB_DIR="${BACKUP_ROOT}/db"

# Postgres connection (override via env if needed)
PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-sisvot_db}"
PGUSER="${PGUSER:-sisuserdb}"
# Set PGPASSWORD in environment before running, or configure ~/.pgpass

mkdir -p "${CODE_DIR}" "${DB_DIR}"

echo "[1/3] Creating code archive..."
CODE_ARCHIVE="${CODE_DIR}/sisvot_code_${TS}.tar.gz"
tar \
  --exclude=".venv" \
  --exclude=".git" \
  --exclude="staticfiles" \
  --exclude="__pycache__" \
  -czf "${CODE_ARCHIVE}" \
  .
echo "Code archived at: ${CODE_ARCHIVE}"

echo "[2/3] Dumping PostgreSQL database ${PGDATABASE}..."
DB_DUMP="${DB_DIR}/sisvot_db_${TS}.sql.gz"
pg_dump -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" "${PGDATABASE}" | gzip -9 > "${DB_DUMP}"
echo "DB dump created at: ${DB_DUMP}"

echo "[3/3] Verifying archives..."
test -s "${CODE_ARCHIVE}" && test -s "${DB_DUMP}" && echo "Backup OK"

echo "Done."

