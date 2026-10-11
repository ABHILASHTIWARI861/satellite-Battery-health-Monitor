#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Run this setup script inside Ubuntu/WSL, not Git Bash or Windows PowerShell." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y gcc-avr avr-libc simavr libsimavr-dev libelf-dev gcc g++ make curl python3-venv python3-dev

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
chmod +x simulator/build_firmware.sh simulator/run_emulator.sh
python -m compileall -q run_dashboard.py src
python - <<'PY'
from fastapi import FastAPI
from reportlab.pdfgen import canvas
import pandas, sklearn, xgboost, yaml, websockets
print('Python dependencies/imports: OK')
print('FastAPI, ReportLab, pandas, scikit-learn, XGBoost, PyYAML, WebSockets: OK')
PY
python simulator/verify_firmware.py

echo
echo 'Setup complete. Start simulator and dashboard in two separate Ubuntu terminals.'
echo 'Terminal 1: bash simulator/run_emulator.sh 7777'
echo 'Terminal 2: source .venv/bin/activate && python run_dashboard.py --no-browser --hitl-port socket://127.0.0.1:7777'
echo 'Browser: http://127.0.0.1:8000/arduino-simulator'
