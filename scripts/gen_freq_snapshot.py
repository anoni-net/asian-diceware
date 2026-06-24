#!/usr/bin/env python3
"""重新產生 vendored 頻率快照 data/sources/freq_en.txt。
Regenerate the vendored frequency snapshot data/sources/freq_en.txt.

這是「開發工具」，不屬於 runtime pipeline。需要 `snapshot` extra
（`uv pip install -e ".[snapshot]"`）。pipeline 本身只讀 vendored 快照、不 import
wordfreq，因此建構可離線重現。
This is a DEV tool, not part of the runtime pipeline. It requires the `snapshot`
extra (`uv pip install -e ".[snapshot]"`). The pipeline itself reads the vendored
snapshot and never imports wordfreq, so builds are reproducible offline.

快照是頻率排序的英文 token 清單（最高頻在前），僅作為「排序輸入」使用
（見 LICENSE-DATA）。輕量預過濾讓檔案變小；真正的正規化在 pipeline（normalize.py）。
The snapshot is a frequency-ordered list of English tokens (most frequent first),
used purely as a *ranking input* (see LICENSE-DATA). Light pre-filtering keeps the
file small; the real normalization happens in the pipeline (normalize.py).
"""

from __future__ import annotations

import re
from pathlib import Path

from wordfreq import top_n_list

POOL_SIZE = 60_000
OUT = Path(__file__).resolve().parent.parent / "data" / "sources" / "freq_en.txt"
# Keep plausible word tokens only; the pipeline re-validates charset/length.
TOKEN_RE = re.compile(r"^[a-z]{2,12}$")


def main() -> None:
    words = top_n_list("en", POOL_SIZE)
    kept = [w for w in words if TOKEN_RE.match(w)]
    header = (
        "# freq_en.txt — frequency-ordered English tokens (most frequent first).\n"
        f"# Source: wordfreq top_n_list('en', {POOL_SIZE}), used as a RANKING input only.\n"
        "# Pre-filter: ^[a-z]{2,12}$. Regenerate with scripts/gen_freq_snapshot.py.\n"
    )
    OUT.write_text(header + "\n".join(kept) + "\n", encoding="utf-8")
    print(f"wrote {len(kept)} words -> {OUT}")


if __name__ == "__main__":
    main()
