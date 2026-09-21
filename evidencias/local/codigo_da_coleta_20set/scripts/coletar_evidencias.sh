#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/coletar_evidencias.py
