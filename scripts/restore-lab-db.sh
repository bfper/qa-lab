#!/usr/bin/env bash
# Restore a production dump into the LAB database and scrub it immediately.
#
# Usage: ./scripts/restore-lab-db.sh ~/dumps/mentoria-2026-09-15.dump
#
# The dump file itself is gitignored and must never leave your machine.
set -euo pipefail

DUMP="${1:?usage: restore-lab-db.sh <dump-file>}"
HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-15432}"
USER="${POSTGRES_USER:-qalab}"
DB="${MENTORIA_DB:-mentoria}"

if [[ "$HOST" != "localhost" && "$HOST" != "127.0.0.1" ]]; then
  echo "ABORT: POSTGRES_HOST is '$HOST'. This script is local-only." >&2
  exit 3
fi

echo "==> restoring $DUMP into $DB@$HOST:$PORT"
PGPASSWORD="${POSTGRES_PASSWORD:-qalab}" pg_restore \
  --host "$HOST" --port "$PORT" --username "$USER" \
  --dbname "$DB" --clean --if-exists --no-owner --no-privileges \
  "$DUMP"

echo "==> anonymizing"
PGPASSWORD="${POSTGRES_PASSWORD:-qalab}" psql \
  --host "$HOST" --port "$PORT" --username "$USER" \
  --dbname "$DB" -v ON_ERROR_STOP=1 -f scripts/anonymize.sql

echo "==> done. Verify before using:"
echo "    psql -h $HOST -p $PORT -U $USER -d $DB -c 'SELECT id, nome, email FROM mentorando LIMIT 5;'"
