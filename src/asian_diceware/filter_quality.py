"""階段 3 — filter_quality（品質過濾）。
Stage 3 — filter_quality.

依序套用：冒犯字（badwords）、同音／難拼排除、專有名詞移除。
Apply, in order: badwords, homophone/hard-spell exclusions, proper-noun removal.

Pin 豁免規則（SPEC §5 stage 3）/ Pin exemption (SPEC §5 stage 3):
- 被 pin 的外來語「豁免」同音／難拼與專有名詞過濾（它們是刻意選入、已詞彙化的
  常見名詞）。
  Pinned loanwords are EXEMPT from the homophone/hard-spell and proper-noun
  filters (they are deliberately chosen, lexicalized common nouns).
- 被 pin 的外來語「不豁免」冒犯字過濾。若一個 pin 同時是冒犯字，視為種子清單錯誤：
  讓建構明確失敗，而不是默默把受保護的 pin 丟掉。
  Pinned loanwords are NOT exempt from the badwords filter. A pinned word that
  is also a badword is a seed-list error: the build fails loudly rather than
  silently dropping a member of the protected pin set.
"""

from __future__ import annotations

from pathlib import Path

from .common import Candidate, data_dir, interim_dir, read_candidates, write_candidates


def load_wordset(path: Path) -> set[str]:
    if not path.exists():
        return set()
    words: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if not w or w.startswith("#"):
                continue
            # 冒犯字清單可能含多 token 片語；我們只比對單一 token。
            # badwords lists may contain multi-token phrases; we only match tokens.
            if " " in w or "-" in w:
                continue
            words.add(w)
    return words


def filter_quality(
    in_path: Path | None = None,
    out_path: Path | None = None,
    badwords_path: Path | None = None,
    quality_path: Path | None = None,
    proper_path: Path | None = None,
) -> Path:
    src = data_dir() / "sources"
    in_path = in_path or (interim_dir() / "normalized.csv")
    out_path = out_path or (interim_dir() / "filtered.csv")
    badwords = load_wordset(badwords_path or (src / "badwords_en.txt"))
    quality = load_wordset(quality_path or (src / "quality_exclude.txt"))
    proper = load_wordset(proper_path or (src / "proper_nouns.txt"))

    kept: list[Candidate] = []
    pinned_badwords: list[str] = []

    for c in read_candidates(in_path):
        if c.word in badwords:
            if c.is_pin:
                pinned_badwords.append(c.word)
            continue  # 冒犯字對所有字一律剔除 / offensive words are dropped for everyone
        if c.is_pin:
            kept.append(c)  # 豁免其餘（可用性）過濾 / exempt from the remaining (usability) filters
            continue
        if c.word in quality:
            continue
        if c.word in proper:
            continue
        kept.append(c)

    if pinned_badwords:
        raise ValueError(
            "pinned loanword(s) appear in the badwords list: "
            + ", ".join(sorted(pinned_badwords))
            + " — fix data/sources/loanwords_seed.csv (a pin must not be offensive)"
        )

    write_candidates(out_path, kept)
    return out_path
