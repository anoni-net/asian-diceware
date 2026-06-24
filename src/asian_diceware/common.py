"""共用工具：路徑、interim 列的資料結構、CSV 讀寫。
Shared helpers: paths, the interim-row schema, and CSV read/write.

「候選列（candidate row）」是流經 pipeline 的單位，為一個純 dict，欄位如下
（CSV 內以字串儲存，讀取時轉型）。
A "candidate row" is the unit that flows through the pipeline. It is a plain dict
with these keys (stored as strings in CSV, coerced on read):

    word         str   小寫 token / lowercase token
    freq_rank    int   0 = 最高頻；外來語若不在頻率快照中給一個很大的哨兵值，
                       使其在組裝時排在所有填充字之後。
                       0 = most frequent; a large sentinel for loanwords absent
                       from the frequency snapshot (so they sort last among fill)
    is_loanword  int   來自 loanwords_seed.csv 為 1，否則 0
                       1 if it came from loanwords_seed.csv, else 0
    decision     str   pin | hold | exclude | ""（只有外來語會帶值）
                       pin | hold | exclude | ""  (only loanwords carry one)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["word", "freq_rank", "is_loanword", "decision"]

# 不在頻率快照中的外來語給這個 rank，使其在組裝時排在所有真實頻率填充字之後。
# Loanwords not found in the frequency snapshot get this rank so they sort after
# all real frequency-ranked fill words during assembly.
NO_FREQ_RANK = 10_000_000


def repo_root() -> Path:
    """專案根目錄（包含 data/、src/、output/ 的那層）。
    Project root (the dir that contains data/, src/, output/)."""
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return repo_root() / "data"


def interim_dir() -> Path:
    d = data_dir() / "interim"
    d.mkdir(parents=True, exist_ok=True)
    return d


def output_dir() -> Path:
    d = repo_root() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class Candidate:
    word: str
    freq_rank: int
    is_loanword: int
    decision: str

    @property
    def is_pin(self) -> bool:
        return self.is_loanword == 1 and self.decision == "pin"


def write_candidates(path: Path, rows: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "word": r.word,
                    "freq_rank": r.freq_rank,
                    "is_loanword": r.is_loanword,
                    "decision": r.decision,
                }
            )


def read_candidates(path: Path) -> list[Candidate]:
    rows: list[Candidate] = []
    with path.open(newline="", encoding="utf-8") as f:
        for d in csv.DictReader(f):
            rows.append(
                Candidate(
                    word=d["word"],
                    freq_rank=int(d["freq_rank"]),
                    is_loanword=int(d["is_loanword"]),
                    decision=d.get("decision", ""),
                )
            )
    return rows
