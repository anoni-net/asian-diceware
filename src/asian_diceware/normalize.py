"""階段 2 — normalize（正規化）。
Stage 2 — normalize.

轉小寫、做 NFC 正規化、去除非 ASCII，再剔除不是 3–9 個小寫 ASCII 字母的字。
被 pin 的外來語本來就乾淨，但同樣走一遍（pin 若在此被剔除，代表種子清單有錯，
值得讓它浮現）。
Lowercase, NFC-normalize, strip non-ASCII, then drop anything that is not
3-9 lowercase ASCII letters. Pinned loanwords are already clean but go through
the same gate (a pin that fails here is a seed-list error worth surfacing).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .common import Candidate, interim_dir, read_candidates, write_candidates

WORD_RE = re.compile(r"^[a-z]{3,9}$")


def normalize_word(raw: str) -> str | None:
    w = unicodedata.normalize("NFC", raw).strip().lower()
    # 盡量去除重音轉成 ASCII，再只保留 a-z。
    # Drop accents -> ASCII where possible, then keep only a-z.
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode("ascii")
    if WORD_RE.match(w):
        return w
    return None


def normalize(in_path: Path | None = None, out_path: Path | None = None) -> Path:
    in_path = in_path or (interim_dir() / "candidates.csv")
    out_path = out_path or (interim_dir() / "normalized.csv")

    seen: set[str] = set()
    kept: list[Candidate] = []
    dropped_pins: list[str] = []

    for c in read_candidates(in_path):
        nw = normalize_word(c.word)
        if nw is None:
            if c.is_pin:
                dropped_pins.append(c.word)
            continue
        if nw in seen:
            # 保留第一筆；若後出現的重複是 pin，把已保留的那筆升級為 pin。
            # Keep the first occurrence; if a later dup is a pin, upgrade the kept row.
            if c.is_pin:
                for k in kept:
                    if k.word == nw and not k.is_pin:
                        k.is_loanword, k.decision = 1, "pin"
            continue
        seen.add(nw)
        kept.append(
            Candidate(
                word=nw, freq_rank=c.freq_rank, is_loanword=c.is_loanword, decision=c.decision
            )
        )

    if dropped_pins:
        raise ValueError(
            "normalize dropped pinned loanword(s) failing ^[a-z]{3,9}$: "
            + ", ".join(sorted(dropped_pins))
            + " — fix data/sources/loanwords_seed.csv"
        )

    write_candidates(out_path, kept)
    return out_path
