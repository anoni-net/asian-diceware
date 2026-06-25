#!/usr/bin/env bash
# 產生可列印的查表小冊（PDF）。用法：./scripts/make_booklet.sh [--size a5|a6] [--font 7]
# Make a printable lookup booklet (PDF). Usage: ./scripts/make_booklet.sh [--size a5|a6] [--font 7]
# 需先安裝 booklet 套件：pip install -e ".[booklet]"（或 uv pip install -e ".[booklet]"）
# Requires the booklet extras: pip install -e ".[booklet]" (or uv pip install ...)
set -euo pipefail
cd "$(dirname "$0")/.."

# macOS：weasyprint 需要 Homebrew 的原生函式庫（pango、gobject 等），補上 dyld 路徑。
# macOS: weasyprint needs Homebrew's native libs (pango, gobject, ...) on the dyld path.
if [ "$(uname)" = "Darwin" ]; then
  BREW_LIB="$(brew --prefix 2>/dev/null)/lib"
  if [ -d "$BREW_LIB" ]; then
    export DYLD_FALLBACK_LIBRARY_PATH="${BREW_LIB}${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"
  fi
fi

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then PY="python3"; fi
"$PY" scripts/make_booklet.py "$@"
