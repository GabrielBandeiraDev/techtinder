#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# SKIP_ALEMBIC=1 se você já rodou supabase/schema.sql no Supabase
if [[ "${SKIP_ALEMBIC:-}" != "1" && ( -n "${SUPABASE_DB_PASSWORD:-}" || -n "${DATABASE_URL:-}" ) ]]; then
  alembic -c alembic.ini upgrade head || {
    echo "[render_start] alembic falhou (schema já existe?). Defina SKIP_ALEMBIC=1 no Render."
    exit 1
  }
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
