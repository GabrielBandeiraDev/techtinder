#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ -n "${SUPABASE_DB_PASSWORD:-}" || -n "${DATABASE_URL:-}" ]]; then
  alembic -c alembic.ini upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
