#!/usr/bin/env bash
# 可重現的端到端建構。用法：./scripts/run_pipeline.sh [TARGET]
# Reproducible end-to-end build. Usage: ./scripts/run_pipeline.sh [TARGET]
# TARGET 預設 7776（完整詞表）。用 1296 跑 v0.1 方法論切片。
# TARGET defaults to 7776 (full list). Use 1296 for the v0.1 methodology slice.
set -euo pipefail

cd "$(dirname "$0")/.."
TARGET="${1:-7776}"

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  PY="python3"
fi

"$PY" -m asian_diceware.cli all --target "$TARGET"
