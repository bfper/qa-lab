#!/bin/bash
# Creates one database per name in LAB_DATABASES. Runs once, on first boot
# of an empty volume. To re-run: docker compose down -v
set -euo pipefail

for db in $(echo "${LAB_DATABASES}" | tr ',' ' '); do
  echo "qa-lab: creating database '${db}'"
  psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname postgres <<-SQL
    CREATE DATABASE "${db}";
    GRANT ALL PRIVILEGES ON DATABASE "${db}" TO "${POSTGRES_USER}";
SQL
done
