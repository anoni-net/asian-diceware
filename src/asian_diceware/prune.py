"""階段 4 — prune（剪枝為唯一可解碼／prefix-free，並保護 pin）。
Stage 4 — prune to a uniquely-decodable (prefix-free) set, pins protected.

Prefix-free 是唯一可解碼的強形式，也是這裡的目標：被收錄的字不可以是另一個被收錄
字的前綴。
Prefix-free is the strong form of unique decodability and the target here: no
accepted word may be a prefix of another accepted word.

優先序（SPEC §5.1），實作為依優先度排序、在 trie 上的貪婪建構：
Precedence (SPEC §5.1), implemented as a priority-ordered greedy build over a trie:

1. pin 集合 P「先」處理。此階段 trie 內只有 pin，因此任何 prefix 衝突都是
   pin↔pin 衝突，無法自動解決：蒐集所有這類配對並讓建構失敗（由人去改
   loanwords_seed.csv）。pin 永不被默默丟棄。
   The pin set P is processed FIRST. Since only pins are in the trie during this
   phase, ANY prefix collision is a pinned↔pinned collision: unresolvable
   automatically. We collect every such pair and FAIL the build (a human edits
   loanwords_seed.csv). A pinned word is never silently dropped.
2. 接著依頻率由高到低（freq_rank 由小到大）處理填充字。與任何已收錄字（pin，
   或更高頻的填充字）衝突的填充字會被丟棄：受保護／更高頻的一方永遠勝出。
   Non-pins are then processed in descending frequency (ascending freq_rank).
   A non-pin that collides with anything already accepted (a pin, or a
   higher-frequency non-pin) is dropped — the protected / higher-frequency side
   always wins.

結果為 prefix-free，且包含 P 的全部成員。
The result is prefix-free and contains all of P.
"""

from __future__ import annotations

from pathlib import Path

from .common import Candidate, interim_dir, read_candidates, write_candidates


class _Node:
    __slots__ = ("children", "end_word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.end_word: str | None = None


class PinnedPrefixCollision(ValueError):
    """兩個被 pin 的字在 prefix-free 限制下衝突（SPEC §5.1 step 3）。
    Two pinned words collide on the prefix-free constraint (SPEC §5.1 step 3)."""


class Trie:
    def __init__(self) -> None:
        self.root = _Node()

    def conflict(self, word: str) -> str | None:
        """回傳與 `word` 衝突的已收錄字，沒有則回傳 None。
        Return an accepted word that conflicts with `word`, else None.

        衝突指：某個已收錄字是 `word` 的前綴，或 `word` 是（或等於）某個已收錄字的前綴。
        A conflict is: an accepted word is a prefix of `word`, OR `word` is a
        prefix of (or equal to) an accepted word.
        """
        node = self.root
        for ch in word:
            if node.end_word is not None:
                # 已收錄字是 `word` 的前綴 / an accepted word is a prefix of `word`
                return node.end_word
            nxt = node.children.get(ch)
            if nxt is None:
                return None  # 路徑分岔，不可能衝突 / path diverges: no conflict possible
            node = nxt
        if node.end_word is not None:
            return node.end_word  # 完全重複 / exact duplicate
        # `word` 在 trie 內走完，代表它是某個更長字的前綴。
        # `word` fully consumed inside the trie -> it is a prefix of a longer word.
        return self._first_below(node)

    @staticmethod
    def _first_below(node: _Node) -> str | None:
        stack = list(node.children.values())
        while stack:
            n = stack.pop()
            if n.end_word is not None:
                return n.end_word
            stack.extend(n.children.values())
        return None

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, _Node())
        node.end_word = word


def prune(in_path: Path | None = None, out_path: Path | None = None) -> Path:
    in_path = in_path or (interim_dir() / "filtered.csv")
    out_path = out_path or (interim_dir() / "decodable.csv")

    rows = read_candidates(in_path)
    pins = sorted((c for c in rows if c.is_pin), key=lambda c: (c.freq_rank, c.word))
    fill = sorted((c for c in rows if not c.is_pin), key=lambda c: (c.freq_rank, c.word))

    trie = Trie()
    survivors: list[Candidate] = []

    # 第一階段：pin。此處任何衝突都是 pin↔pin。
    # Phase 1: pins. Any conflict here is pinned<->pinned.
    collisions: list[tuple[str, str]] = []
    for c in pins:
        other = trie.conflict(c.word)
        if other is not None:
            collisions.append((other, c.word))
            continue
        trie.insert(c.word)
        survivors.append(c)
    if collisions:
        pairs = "; ".join(f"{a} <-> {b}" for a, b in collisions)
        raise PinnedPrefixCollision(
            "pinned loanwords collide on the prefix-free constraint: "
            + pairs
            + " — edit data/sources/loanwords_seed.csv (flip one pin -> hold/exclude)"
        )

    # 第二階段：填充字，高頻優先；丟棄衝突中較低頻的一方。
    # Phase 2: fill words, highest frequency first; drop the colliding lower side.
    for c in fill:
        if trie.conflict(c.word) is not None:
            continue
        trie.insert(c.word)
        survivors.append(c)

    write_candidates(out_path, survivors)
    return out_path
