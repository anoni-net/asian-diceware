#!/usr/bin/env bash
# 稽核一份建好的詞表。用法：./scripts/audit.sh [TARGET]
# Audit a built wordlist. Usage: ./scripts/audit.sh [TARGET]
# 一律跑 Python 稽核；若有安裝 Rust 的 `wla` 也會一併跑。
# Runs the Python audit (always) and the Rust `wla` auditor if it is installed.
set -euo pipefail

cd "$(dirname "$0")/.."
TARGET="${1:-7776}"
LIST="output/asian_diceware_${TARGET}.txt"

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then PY="python3"; fi

"$PY" -m asian_diceware.cli validate --target "$TARGET"

if command -v wla >/dev/null 2>&1; then
  echo
  echo "=== wla (Word List Auditor) ==="
  wla "$LIST"
else
  echo
  echo "note: 'wla' not installed (cargo install wla) — skipped external audit."
  echo "      'wla' 未安裝，略過外部稽核。"
  echo "      (the system /usr/bin/tidy is HTML tidy, NOT sts10/tidy — do not use it here.)"
  echo "      （系統的 /usr/bin/tidy 是 HTML tidy，不是 sts10/tidy，請勿在此使用。）"
fi
