"""階段 1 — collect（蒐集）。
Stage 1 — collect.

載入頻率快照與 loanwords_seed.csv，輸出 candidates.csv。
Load the frequency snapshot + loanwords_seed.csv and emit candidates.csv.

被 pin 的外來語若同時出現在頻率快照中，保留其真實頻率 rank，但標記為
is_loanword=1／decision=pin（讓 prune 保護它）。若不在快照中，則以哨兵 rank 加入，
使其在組裝時排在所有填充字之後。只有 decision=pin 的外來語會進入候選池；
hold／exclude 不進（被 hold 的字若本身是常見英文，仍可能以一般填充字身分出現）。
A pinned loanword that also appears in the frequency snapshot keeps its real
frequency rank but is marked is_loanword=1/decision=pin (so prune protects it).
A pinned loanword absent from the snapshot is added with a sentinel rank so it
sorts after all real fill words during assembly. Only `decision=pin` loanwords
enter the candidate pool; `hold`/`exclude` rows do not (a held word may still
appear as ordinary fill if it is common English in the frequency snapshot).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .common import NO_FREQ_RANK, Candidate, data_dir, interim_dir, write_candidates


def load_freq(path: Path) -> list[str]:
    words: list[str] = []
    seen: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w or w.startswith("#"):
                continue
            if w in seen:
                continue
            seen.add(w)
            words.append(w)
    return words


def load_pinned_loanwords(path: Path) -> dict[str, str]:
    """回傳 decision 為 pin 的列 {word: decision}。
    Return {word: decision} for rows with decision in {pin}."""
    pins: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row or row[0].strip().startswith("#"):
                continue
            if row[0].strip() == "word" or len(row) < 6:
                continue
            word = row[0].strip().lower()
            decision = row[5].strip().lower()
            if decision == "pin":
                pins[word] = decision
    return pins


def collect(
    freq_path: Path | None = None,
    seed_path: Path | None = None,
    out_path: Path | None = None,
    pool_size: int | None = None,
) -> Path:
    freq_path = freq_path or (data_dir() / "sources" / "freq_en.txt")
    seed_path = seed_path or (data_dir() / "sources" / "loanwords_seed.csv")
    out_path = out_path or (interim_dir() / "candidates.csv")

    freq = load_freq(freq_path)
    if pool_size is not None:
        freq = freq[:pool_size]
    pins = load_pinned_loanwords(seed_path)

    rank_of = {w: i for i, w in enumerate(freq)}
    rows: list[Candidate] = []

    for i, w in enumerate(freq):
        if w in pins:
            rows.append(Candidate(word=w, freq_rank=i, is_loanword=1, decision="pin"))
        else:
            rows.append(Candidate(word=w, freq_rank=i, is_loanword=0, decision=""))

    # 不在頻率快照中的 pin 外來語：以哨兵 rank 補上。
    # Pinned loanwords missing from the frequency snapshot: append with sentinel rank.
    for w in pins:
        if w not in rank_of:
            rows.append(Candidate(word=w, freq_rank=NO_FREQ_RANK, is_loanword=1, decision="pin"))

    write_candidates(out_path, rows)
    return out_path
