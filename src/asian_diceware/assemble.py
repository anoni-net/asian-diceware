"""階段 5 — assemble（組裝最終詞表並輸出產物）。
Stage 5 — assemble the final list and emit outputs.

先放入全部被 pin 的存活字（受保護集合 P），再用最高頻的非 pin 存活字填充，直到
詞表「恰好」為 target 個字（SPEC §5.1 step 4）。最終詞表以字母順序排序輸出：
Start with all pinned survivors (the protected set P), then fill with the
highest-frequency non-pinned survivors until the list is exactly `target` words
(SPEC §5.1 step 4). The final list is written alphabetically sorted:

  output/asian_diceware_<target>.txt        一行一字 / one word per line
  output/asian_diceware_<target>_dice.txt   "<roll>\t<word>"，base-6 數字 1-6

另外把帶有每字 metadata 的 assembled.csv 留在 data/interim/ 供稽核。
An assembled.csv (with per-word metadata) is kept in data/interim/ for the audit.
"""

from __future__ import annotations

import math
from pathlib import Path

from .common import Candidate, interim_dir, output_dir, read_candidates, write_candidates


def dice_digits(target: int) -> int | None:
    """1:1 對應所需的骰子數；target 不是 6 的次方則回傳 None。
    Number of dice for a 1:1 mapping, or None if target is not a power of 6."""
    n = round(math.log(target, 6))
    return n if 6**n == target else None


def to_roll(index: int, n_dice: int) -> str:
    """以數字 1-6 表示 `index` 的 base-6，補零到 n_dice 位。
    Base-6 representation of `index` using digits 1-6, padded to n_dice."""
    digits = []
    for _ in range(n_dice):
        index, rem = divmod(index, 6)
        digits.append(str(rem + 1))
    return "".join(reversed(digits))


def assemble(
    target: int,
    in_path: Path | None = None,
    out_txt: Path | None = None,
    out_dice: Path | None = None,
) -> tuple[Path, Path | None]:
    in_path = in_path or (interim_dir() / "decodable.csv")
    out_txt = out_txt or (output_dir() / f"asian_diceware_{target}.txt")
    out_dice = out_dice or (output_dir() / f"asian_diceware_{target}_dice.txt")

    rows = read_candidates(in_path)
    pins = [c for c in rows if c.is_pin]
    fill = sorted((c for c in rows if not c.is_pin), key=lambda c: (c.freq_rank, c.word))

    if len(pins) > target:
        raise ValueError(
            f"pin set ({len(pins)}) exceeds target ({target}); "
            "reduce pins in loanwords_seed.csv or raise the target"
        )

    chosen = pins + fill[: target - len(pins)]
    if len(chosen) < target:
        raise ValueError(
            f"only {len(chosen)} words available, need {target}. "
            "Widen the candidate pool (larger freq snapshot / higher --pool-size) "
            "and re-run from collect."
        )

    words_sorted = sorted(c.word for c in chosen)
    out_txt.write_text("\n".join(words_sorted) + "\n", encoding="utf-8")

    # 骰子對應（只有 target 為 6 的次方時才有意義）。
    # Dice mapping (only meaningful when target is a power of 6).
    n_dice = dice_digits(target)
    dice_path: Path | None = None
    if n_dice is not None:
        lines = [f"{to_roll(i, n_dice)}\t{w}" for i, w in enumerate(words_sorted)]
        out_dice.write_text("\n".join(lines) + "\n", encoding="utf-8")
        dice_path = out_dice

    # 保留 metadata 供稽核，順序與最終詞表一致。
    # Keep metadata for the audit, ordered like the final list.
    meta = {c.word: c for c in chosen}
    assembled = [meta[w] for w in words_sorted]
    write_candidates(interim_dir() / "assembled.csv", assembled)

    return out_txt, dice_path


def assembled_meta() -> list[Candidate]:
    return read_candidates(interim_dir() / "assembled.csv")
