#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Apenas dependências. NÃO rode alembic aqui: o build do Render não acessa o Supabase
# (erro "Network is unreachable"). Migrações ficam em render_start.sh.
pip install -r requirements.txt

echo "[render_build] OK — migrações rodam no start (render_start.sh)."
