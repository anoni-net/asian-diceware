"""Pipeline 行為測試：pin/prune 優先序（SPEC §5.1）與骰子對應。
Pipeline behaviour tests: the pin/prune precedence (SPEC §5.1) and dice mapping.

這些測試使用小型合成輸入，不會碰到 vendored 資料。
These run on small synthetic inputs and do not touch the vendored data.
"""

from __future__ import annotations

import pytest

from asian_diceware import prune
from asian_diceware.assemble import dice_digits, to_roll
from asian_diceware.common import Candidate, read_candidates, write_candidates


def _write(path, rows):
    write_candidates(path, rows)
    return path


def test_pin_protected_over_higher_freq_fill(tmp_path):
    # 'cat' is pinned but lower frequency than the non-pin 'cats' that contains it.
    # Prefix-free must keep the pin and drop the non-pinned colliding word.
    rows = [
        Candidate("cats", freq_rank=1, is_loanword=0, decision=""),
        Candidate("cat", freq_rank=50, is_loanword=1, decision="pin"),
        Candidate("dog", freq_rank=2, is_loanword=0, decision=""),
    ]
    out = prune.prune(_write(tmp_path / "in.csv", rows), tmp_path / "out.csv")
    words = {c.word for c in read_candidates(out)}
    assert "cat" in words  # pin survives
    assert "cats" not in words  # non-pin colliding side dropped
    assert "dog" in words


def test_two_nonpins_drop_lower_freq(tmp_path):
    # No pins involved: the higher-frequency (lower rank) word wins.
    rows = [
        Candidate("art", freq_rank=2, is_loanword=0, decision=""),
        Candidate("arts", freq_rank=1, is_loanword=0, decision=""),
    ]
    out = prune.prune(_write(tmp_path / "in.csv", rows), tmp_path / "out.csv")
    words = {c.word for c in read_candidates(out)}
    # 'arts' (rank 1) processed first; 'art' is a prefix of it -> dropped.
    assert words == {"arts"}


def test_pinned_pinned_collision_fails_loudly(tmp_path):
    rows = [
        Candidate("ramen", freq_rank=10, is_loanword=1, decision="pin"),
        Candidate("rame", freq_rank=20, is_loanword=1, decision="pin"),
    ]
    with pytest.raises(prune.PinnedPrefixCollision) as exc:
        prune.prune(_write(tmp_path / "in.csv", rows), tmp_path / "out.csv")
    assert "rame" in str(exc.value) and "ramen" in str(exc.value)


def test_dice_digits():
    assert dice_digits(1296) == 4
    assert dice_digits(7776) == 5
    assert dice_digits(1000) is None  # not a power of 6


def test_to_roll_endpoints():
    assert to_roll(0, 5) == "11111"
    assert to_roll(7775, 5) == "66666"
    assert to_roll(0, 4) == "1111"
    assert to_roll(1295, 4) == "6666"
    # index 6 -> base6 '00010' -> digits+1 -> '11121'
    assert to_roll(6, 5) == "11121"
