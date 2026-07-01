#!/usr/bin/env bash
# ── BG Remover startup script for Pterodactyl ────────────────────────────────
set -e

echo "==> Installing dependencies…"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "==> Pre-downloading BiRefNet model (first run only, ~500 MB)…"
python - <<'PYEOF'
from rembg import new_session
new_session("birefnet-general")
print("Model ready.")
PYEOF

echo "==> Starting server on port ${PORT:-3000}…"
exec python app.py
