#!/usr/bin/env bash
set -euo pipefail
# Sempre executa a partir de backend/ (onde estão alembic.ini e app/)
cd "$(dirname "$0")"

pip install -r requirements.txt

if [[ -n "${SUPABASE_DB_PASSWORD:-}" || -n "${DATABASE_URL:-}" ]]; then
  alembic -c alembic.ini upgrade head
else
  echo "[render_build] Sem SUPABASE_DB_PASSWORD/DATABASE_URL — pulando migrações no build."
fi
