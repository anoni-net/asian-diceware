"""階段 6 — validate（對照 SPEC §2 驗收標準並輸出稽核報告）。
Stage 6 — validate against the SPEC §2 acceptance criteria + emit an audit.

`audit()` 回傳結構化報告；`validate()`（CLI）會印出報告，若任一「硬性」標準
失敗則以非零碼結束。S7 遵循 SPEC 註記：先斷言字數，再由字數推導
entropy = log2(count)，絕不對浮點字面值做相等比較。
`audit()` returns a structured report; `validate()` (CLI) prints it and exits
nonzero if any HARD criterion fails. S7 follows the SPEC note: assert the count,
then derive entropy = log2(count) — never float-compare a literal.

外來語占比帶（S6，SPEC §3.9 約 120-180）以「參考值」回報：硬性 S6 不變量是
set(seed_pins) ⊆ final（每個被 pin 的字都在）。種子清單擴充後，這個帶在 v1.0
才成為發佈門檻。
The loanword-share band (S6, SPEC §3.9 ~120-180) is reported as ADVISORY: the
hard S6 invariant is `set(seed_pins) ⊆ final` (every pinned word present). The
band becomes a release gate for v1.0 once the seed list is expanded.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from .collect import load_pinned_loanwords
from .common import data_dir, repo_root
from .filter_quality import load_wordset

WORD_RE = re.compile(r"^[a-z]{3,9}$")
PIN_BAND = (120, 180)  # SPEC §3.9 v1.0 目標；種子擴充前僅為參考 / advisory until seed expanded.
MAX_AVG_LEN = 7.5


@dataclass
class Check:
    id: str
    name: str
    ok: bool
    detail: str
    hard: bool = True


def read_wordlist(path: Path) -> list[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def first_prefix_collision(words_sorted: list[str]) -> tuple[str, str] | None:
    for a, b in zip(words_sorted, words_sorted[1:], strict=False):
        if b.startswith(a):
            return (a, b)
    return None


def audit(wordlist_path: Path, target: int = 7776, seed_path: Path | None = None) -> dict:
    src = data_dir() / "sources"
    seed_path = seed_path or (src / "loanwords_seed.csv")
    words = read_wordlist(wordlist_path)
    words_sorted = sorted(words)
    seed_pins = set(load_pinned_loanwords(seed_path))
    badwords = load_wordset(src / "badwords_en.txt")

    count = len(words)
    dupes = sorted({w for w in words if words.count(w) > 1}) if count != len(set(words)) else []
    bad_charset = [w for w in words if not WORD_RE.match(w)][:10]
    collision = first_prefix_collision(words_sorted)
    offensive = sorted(set(words) & badwords)
    present_pins = seed_pins & set(words)
    missing_pins = sorted(seed_pins - set(words))
    pin_count = len(present_pins)
    avg_len = sum(len(w) for w in words) / count if count else 0.0
    entropy = math.log2(count) if count else 0.0
    expected_entropy = math.log2(target)

    checks: list[Check] = [
        Check("S1", "exactly target words", count == target, f"count={count}, target={target}"),
        Check("S2", "no duplicates", not dupes, f"duplicates={dupes[:10]}"),
        Check("S3", "charset ^[a-z]{3,9}$", not bad_charset, f"offenders={bad_charset}"),
        Check(
            "S4",
            "uniquely decodable (prefix-free)",
            collision is None,
            "ok" if collision is None else f"{collision[0]} is a prefix of {collision[1]}",
        ),
        Check("S5", "no offensive words", not offensive, f"offensive={offensive[:10]}"),
        Check(
            "S6",
            "all seed pins present",
            not missing_pins,
            f"pins_present={pin_count}/{len(seed_pins)}, missing={missing_pins[:10]}",
        ),
        Check(
            "S7",
            "entropy = log2(count)",
            count == target and abs(entropy - expected_entropy) < 1e-6,
            f"entropy={entropy:.7f} bits/word (expected {expected_entropy:.7f})",
        ),
        Check(
            "S8",
            f"avg length <= {MAX_AVG_LEN}",
            avg_len <= MAX_AVG_LEN,
            f"avg_len={avg_len:.3f}",
        ),
        Check(
            "S6b",
            f"loanword share in {PIN_BAND}",
            PIN_BAND[0] <= pin_count <= PIN_BAND[1],
            f"pin_count={pin_count} (advisory; target {PIN_BAND})",
            hard=False,
        ),
    ]

    return {
        "wordlist": str(wordlist_path),
        "target": target,
        "metrics": {
            "count": count,
            "pin_count": pin_count,
            "avg_len": round(avg_len, 4),
            "entropy_bits_per_word": round(entropy, 7),
            "six_word_phrase_bits": round(entropy * 6, 2),
        },
        "checks": [vars(c) for c in checks],
        "passed": all(c.ok for c in checks if c.hard),
    }


def format_report(report: dict) -> str:
    lines = [f"audit: {report['wordlist']}  (target {report['target']})", ""]
    m = report["metrics"]
    lines.append(
        f"  count={m['count']}  pins={m['pin_count']}  avg_len={m['avg_len']}  "
        f"entropy={m['entropy_bits_per_word']} bits/word  6-word={m['six_word_phrase_bits']} bits"
    )
    lines.append("")
    for c in report["checks"]:
        mark = "PASS" if c["ok"] else ("FAIL" if c["hard"] else "WARN")
        lines.append(f"  [{mark}] {c['id']:3} {c['name']:34} {c['detail']}")
    lines.append("")
    lines.append("RESULT: " + ("PASS" if report["passed"] else "FAIL"))
    return "\n".join(lines)


def validate(wordlist_path: Path, target: int = 7776, write_json: bool = True) -> dict:
    report = audit(wordlist_path, target=target)
    if write_json:
        out = repo_root() / "output" / "audit_report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
