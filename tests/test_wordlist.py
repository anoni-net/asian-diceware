"""驗收測試 S1-S8（SPEC §2），對一份剛建好的詞表執行。
Acceptance tests S1-S8 (SPEC §2), run against a freshly built list.

建構目標設小（1296 = 6^4，即 v0.1 切片），讓測試快速且完全離線。同一組斷言原封
不動套用到 7776 詞表，只需改 TARGET。S7 遵循 SPEC 註記：先斷言字數，再推導 entropy。
The build target is small (1296 = 6^4, the v0.1 slice) so the suite is fast and
fully offline. The same assertions apply unchanged to the 7776 list; only TARGET
changes. S7 follows the SPEC note: assert the count, then derive entropy.
"""

from __future__ import annotations

import math

import pytest

from asian_diceware import assemble, collect, filter_quality, normalize, prune, validate
from asian_diceware.common import data_dir
from asian_diceware.filter_quality import load_wordset

TARGET = 1296


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> dict:
    """跑一次完整 pipeline，回傳路徑與解析後的字。
    Run the full pipeline once and return paths + parsed words."""
    collect.collect()
    normalize.normalize()
    filter_quality.filter_quality()
    prune.prune()
    txt, _dice = assemble.assemble(target=TARGET)
    words = validate.read_wordlist(txt)
    return {"txt": txt, "words": words}


def test_exactly_1296(built):  # S1
    assert len(built["words"]) == TARGET


def test_no_duplicates(built):  # S2
    words = built["words"]
    assert len(words) == len(set(words))


def test_charset(built):  # S3
    assert all(validate.WORD_RE.match(w) for w in built["words"])


def test_uniquely_decodable(built):  # S4
    collision = validate.first_prefix_collision(sorted(built["words"]))
    assert collision is None, f"{collision} violates prefix-free"


def test_no_offensive(built):  # S5
    badwords = load_wordset(data_dir() / "sources" / "badwords_en.txt")
    assert set(built["words"]) & badwords == set()


def test_loanword_quota(built):  # S6
    seed_pins = set(collect.load_pinned_loanwords(data_dir() / "sources" / "loanwords_seed.csv"))
    final = set(built["words"])
    # 硬性不變量（SPEC §5.1 step 5）：每個被 pin 的字都在。
    # Hard invariant (SPEC §5.1 step 5): every pinned word is present.
    assert seed_pins.issubset(final), f"missing pins: {sorted(seed_pins - final)}"
    pin_count = len(seed_pins & final)
    assert 0 < pin_count <= TARGET


def test_entropy(built):  # S7 — per SPEC note: assert count, then derive entropy
    words = built["words"]
    assert len(words) == TARGET
    entropy = math.log2(len(words))
    assert abs(entropy - math.log2(TARGET)) < 1e-6


def test_length_distribution(built):  # S8
    words = built["words"]
    avg = sum(len(w) for w in words) / len(words)
    assert avg <= validate.MAX_AVG_LEN
