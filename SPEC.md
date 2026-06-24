# SPEC.md — asian-diceware

**Status:** v0.2 implemented (as of 2026-06-24). Pipeline + S1-S8 tests green;
the 160-word pin set is frozen and dictionary-verified. Remaining work toward
v1.0 is tracked in §9 / §10. Began as a pre-implementation handoff spec; kept as
the living design reference.
**Audience:** an implementer (human or Claude Code) starting from an empty repo.
**This file is self-contained.** You do not need to read any external research
report to implement the project. Everything required is here.

---

## 1. Goal

Produce a **7,776-word, EFF-compatible English Diceware wordlist** that blends:

- **(a)** high-frequency, easy-to-spell English words familiar to English users
  in Taiwan / the Sinophone region (low memorization + typing burden), and
- **(b)** dictionary-attested **Asian loanwords** already absorbed into English
  (e.g. `tofu`, `typhoon`, `ramen`, `kimchi`, `karaoke`, `tsunami`).

The list is publishable as a standalone open-source artifact and may later feed
an AnonTicket-style code-phrase generator. It must match EFF's security and
usability properties so it is a drop-in alternative to the EFF Large Wordlist.

Non-goal (v1.0): romanized Mandarin/Zhuyin syllable lists. That is a separate
future sub-project (see §11). v1.0 contains **only English-dictionary words**.

---

## 2. Wordlist specification (acceptance criteria)

The final `output/asian_diceware_7776.txt` MUST satisfy ALL of:

| # | Property | Requirement | How verified |
|---|----------|-------------|--------------|
| S1 | Count | exactly 7776 lines/words | `test_exactly_7776` |
| S2 | Uniqueness | no duplicates | `test_no_duplicates` |
| S3 | Charset | each word matches `^[a-z]{3,9}$` | `test_charset` |
| S4 | Decodability | uniquely decodable (ideally prefix-free) | `test_uniquely_decodable` + `wla` |
| S5 | No offensive | empty intersection with badwords list | `test_no_offensive` |
| S6 | Loanword quota | every `decision=pin` loanword present; total pinned in target range | `test_loanword_quota` |
| S7 | Entropy | `log2(7776)` ≈ 12.925 bits/word (informational) | `test_entropy` |
| S8 | Avg length | mean word length ≤ 7.5 | `test_length_distribution` |

Diceware math (informational): 7776 = 6^5; log2(7776) = 12.9248125 bits/word;
a six-word phrase ≈ 77.5 bits. The list size MUST be exactly 7776 so each
5-die roll maps 1:1 to a word with no bias and no wasted rolls.

> **S7 implementation note (do NOT float-compare):**
> `test_entropy` MUST assert `len(words) == 7776` and then compute
> `entropy = math.log2(len(words))` and assert
> `abs(entropy - 12.9248125) < 1e-6`. Never write `log2(len) == 12.925`
> as a literal float equality — it is not a meaningful test and will be
> brittle. The real invariant is the count (S1); entropy follows from it.

---

## 3. Design criteria

**EFF-derived (apply to ALL words):**
1. Length 3–9 letters. No 1–2 letter words.
2. Prefer high-recognition, high-concreteness words.
3. Remove profane / slur / sensitive / strongly-negative words (badwords filter).
4. Remove hard-to-spell words and homophones.
5. No proper nouns (exception: loanwords now lexicalized as common nouns).
6. Uniquely decodable: no word is an exact prefix of another (prefix-free is
   the strong form and the target).

**Project-specific (additional):**
7. Loanwords must be **single tokens** (no space, no hyphen) AND have
   dictionary backing (OED / Merriam-Webster / Cambridge). Space/hyphen forms
   (`feng shui`, `kung fu`, `dim sum`) are excluded at source.
8. Avoid romanization ambiguity: do NOT transliterate Mandarin ourselves
   (Hanyu Pinyin vs Wade-Giles vs Tongyong coexist in Taiwan). Only accept
   loanwords whose English spelling is already dictionary-fixed.
9. Loanword share: v1.0 target ~120–180 pinned loanwords (~1.5–2.3%).
   Long-term ceiling ~3–8% (~250–600). Usability beats cultural coverage when
   they conflict.

When criteria conflict, resolution order is: **exclude on space/hyphen →
exclude on length → exclude on strong spelling variant → resolve prefix
collisions via §5 → exclude on offensiveness.**

---

## 4. Data sources (and how to obtain them in a restricted sandbox)

> The build environment may have **allowlisted network only** (GitHub, PyPI,
> crates.io reachable; arbitrary domains may not be). Prefer sources that are
> pip-installable or live on GitHub raw, and **vendor them into `data/sources/`
> so the build is reproducible offline.**

| Source | Use | Acquisition | License note |
|--------|-----|-------------|--------------|
| `wordfreq` (PyPI) | English frequency ranking | `pip install wordfreq` | MIT; data CC-BY-SA / others — check before redistributing derived freq data |
| `google-10000-english` (GitHub: first20hours) | base high-freq seed | vendor the raw `.txt` | MIT-ish / public sources |
| SUBTLEX-US (GitHub: words/subtlex-word-frequencies) | freq corpus | vendor JSON/txt | check repo license |
| `loanwords_seed.csv` (this repo) | curated loanwords | already in `data/sources/` | this project |
| badwords list (e.g. LDNOOBW, or ulif/diceware `--no-offensive`) | offensive filter | vendor txt | check license |

**License hygiene:** if you use a CC-BY-SA frequency source to *derive* the
final list, the derived list inherits SA. To keep the output under CC-BY-4.0 or
CC0 (project preference, see §8), use permissive/public-domain frequency
sources, or use the freq source only for *ranking* (a process input) and
document that the words themselves are common English not copied from a
copyrighted compilation. When unsure, prefer `wordfreq` for ranking + a
permissive base list for membership.

---

## 5. Build pipeline (six stages) + the pin/prune precedence

Each stage reads from `data/interim/` and writes the next file there; the CLI
(`src/asian_diceware/cli.py`) chains them. `scripts/run_pipeline.sh` runs end to
end and is the reproducible entry point.

1. **collect** (`collect.py`): load frequency source(s) + `loanwords_seed.csv`;
   emit `candidates.csv` (word, freq_rank, is_loanword, decision).
2. **normalize** (`normalize.py`): lowercase, strip non-ASCII, NFC, drop
   length<3 or >9, drop anything with non-`[a-z]`. Loanwords are already clean
   but run them through too.
3. **filter_quality** (`filter_quality.py`): apply badwords, hard-to-spell,
   homophone, and proper-noun filters. **Loanwords with `decision=pin` are
   exempt from the proper-noun filter** (they are lexicalized) but NOT exempt
   from the badwords filter.
4. **prune** (`prune.py`): make the set uniquely decodable. See precedence below.
5. **assemble** (`assemble.py`): pin loanwords first, then fill to exactly 7776
   by frequency rank. See precedence below.
6. **validate** (`validate.py` + `tests/`): enforce §2 acceptance criteria and
   emit an audit report.

### 5.1 PIN vs PRUNE precedence (this resolves the main ambiguity)

The conflict: a pinned loanword may be a prefix of (or prefixed by) a
high-frequency word, and naive pruning could delete the pinned word.

**Rule — pinned words are protected, the other side of the collision yields:**

1. Build the **pin set** P = all `decision=pin` loanwords (post §3/§4 filtering).
   P is sacred: no stage may drop a member of P.
2. During **prune** (stage 4), run prefix/decodability resolution with P marked
   as **protected**. When a prefix collision involves a pinned word and a
   non-pinned word, **drop the non-pinned word**. When a collision is between
   two non-pinned words, drop the lower-frequency one (standard Schlinkert /
   prefix pruning).
3. If a collision is between **two pinned words** (e.g. both loanwords, one a
   prefix of the other), that is unresolvable automatically: **fail the build
   with a clear error listing the offending pair**, and a human edits
   `loanwords_seed.csv` (change one `pin`→`hold`/`exclude`). Do not silently
   drop a pinned word.
4. **assemble** (stage 5): start the final list with all of P, then add
   non-pinned survivors in descending frequency until the list hits exactly
   7776. If P + survivors < 7776, widen the candidate pool (lower the freq
   cutoff) and re-run prune; if > 7776 after pinning, drop lowest-frequency
   non-pinned words.
5. Invariant checked in tests: `set(P).issubset(set(final))` (this is S6).

> Practical consequence: keep |P| comfortably under the target (≤180) so step 4
> always has room to fill to 7776 with clean high-frequency English words.

---

## 6. Tooling — pinned commands (don't reinvent)

Use the Rust tools `tidy` and `wla` for decodability + audit; use Python only
for curation and orchestration. Install:

```bash
cargo install tidy        # https://github.com/sts10/tidy
cargo install wla         # https://github.com/sts10/wla  (Word List Auditor)
```

**Prefix-free pruning + whittle to 7776 with a protected pin list.**
`tidy` supports removing prefix words and cutting to a target size. The exact
flags must be confirmed against the installed version (`tidy --help`); the
intended operations are:

```bash
# 1) Remove words that are prefixes of other words, normalize, dedupe:
tidy --remove-prefix-words --to-lowercase --remove-nonalphanumeric \
     --sort --dedup -o data/interim/decodable.txt data/interim/filtered.txt

# 2) Whittle to exactly 7776 (frequency-ordered input recommended):
tidy --whittle-to 7776 -o output/asian_diceware_7776.txt data/interim/decodable.txt
```

> **Important:** `tidy` does not know about our pin set. Two safe integration
> options — pick ONE and document it:
>
> - **(A) Python-side prune (recommended):** implement prefix/Sardinas–Patterson
>   pruning in `prune.py` with P protected (per §5.1). Use `wla` only to *audit*
>   the result. This keeps pin logic in one place and avoids fighting `tidy`'s
>   ordering.
> - **(B) tidy-side prune:** feed `tidy` an input where pinned words are sorted
>   first AND verify afterward that no pinned word was removed (re-add + re-check
>   if so). More moving parts; only use if `prune.py` becomes a bottleneck.

**Audit the final list (must pass before release):**

```bash
wla output/asian_diceware_7776.txt
```

Expected `wla` output to confirm: length 7776, uniquely decodable = true,
mean word length ≤ 7.5, entropy per word ≈ 12.925 bits, free of prefix words
(if prefix-free target met), no duplicate words.

---

## 7. Repo layout

```
asian-diceware/
├── README.md  LICENSE  LICENSE-DATA  CONTRIBUTING.md  SPEC.md  CHANGELOG.md
├── pyproject.toml                      # ruff + pytest config
├── data/
│   ├── sources/                        # vendored inputs (freq lists, badwords)
│   │   └── loanwords_seed.csv          # <-- canonical loanword data (in repo)
│   ├── interim/                        # pipeline scratch (gitignored)
│   └── output/                         # mirror of top-level output/ if preferred
├── output/
│   ├── asian_diceware_7776.txt         # plain wordlist (one word per line)
│   ├── asian_diceware_7776_dice.txt    # "11111\tword" five-digit roll + tab + word
│   └── asian_diceware_7776.pdf         # printable (optional, v1.x)
├── src/asian_diceware/
│   ├── collect.py normalize.py filter_quality.py prune.py assemble.py
│   ├── validate.py  cli.py
├── scripts/
│   ├── run_pipeline.sh                 # end-to-end reproducible build
│   └── audit.sh                        # wla wrapper
└── tests/
    ├── test_wordlist.py                # S1–S8
    └── test_pipeline.py
```

Dice-mapping for `_dice.txt`: enumerate the sorted final list and assign each
word the base-6 representation of its index using digits 1–6 (index 0 → `11111`,
index 7775 → `66666`).

---

## 8. Licensing

- **Wordlist data** (`output/*`, `loanwords_seed.csv`): **CC-BY-4.0** (matches
  EFF / Tails convention, high compatibility) — or CC0 if you want zero
  friction. Put this in `LICENSE-DATA`.
- **Code** (`src/`, `scripts/`, `tests/`): **MIT** (or GPLv3 if copyleft
  desired). Put this in `LICENSE`.
- "Diceware" is Arnold Reinhold's trademark — describe the project as
  "Diceware-style / Diceware-compatible" and attribute EFF/Reinhold prior art
  in README. Avoid copying any CC-BY-SA wordlist verbatim if you want to keep
  output under CC-BY/CC0.

---

## 9. Task breakdown (implementation order)

- [x] **T1** Repo skeleton: `pyproject.toml`, ruff+pytest config, MIT `LICENSE`
      + CC-BY-4.0 `LICENSE-DATA`, all module files, `data/`, `output/`. (CI
      runner not yet wired — pending a remote; ruff + pytest run locally.)
- [x] **T2** `loanwords_seed.csv` verified: all **160 pins** confirmed against
      live OED/MW/Cambridge entries and flagged `verified`; +71 dictionary-
      attested pins added, balanced across languages; pin set frozen at 160
      (within the ~120–180 target). 65 candidates parked as `hold` for review.
- [x] **T3** `collect.py`: load vendored freq snapshot + seed CSV → `candidates.csv`.
- [x] **T4** `normalize.py`: case/ASCII/NFC/length filters.
- [x] **T5** `filter_quality.py`: badwords + homophone/hard-spell + proper-noun
      (pins exempt from the latter two, not from badwords). Homophone/proper-noun
      lists are functional starter sets, extensible in future curation.
- [x] **T6** `prune.py`: prefix-free pruning with P protected (§5.1, option A,
      trie-based). Fails loudly on pinned–pinned collision (covered by a test).
- [x] **T7** `assemble.py`: pin P, fill by frequency to exactly the target.
- [x] **T8** `validate.py` + `tests/`: S1–S8 green (13 tests); `test_entropy`
      follows the §2 pattern (assert count, then derive entropy).
- [~] **T9** Outputs: plain list + `_dice.txt` produced for 1296 and 7776;
      `audit.sh` wraps `wla` (skips gracefully if absent). PENDING: install
      cargo + run the `wla` external audit; optional PDF.
- [~] **T10** README / CONTRIBUTING / CHANGELOG done (bilingual zh-TW + English).
      Tagged **v0.2** (PGP-signed). PENDING: v1.0 tag once T9 + release land.

---

## 10. Milestones

- **v0.1 — ✅ done.** Pipeline runs end-to-end producing a small list (1296
  words, 4 dice) + passing tests — methodology proven.
- **v0.2 — ✅ done (tagged, PGP-signed).** Loanword curation complete (T2); the
  160-pin set is frozen and dictionary-verified. The full 7776 list also builds
  and passes S1–S8.
- **v1.0 — in progress.** Remaining: `wla` external audit passes, (optional) PDF,
  set a remote + publish CC-BY, tag v1.0. The 7776 list already passes all
  S1–S8 plus the advisory loanword-share band.
- **v1.x** usability feedback, loanword-share tuning, AnonTicket integration test.

---

## 11. Future directions (out of scope for v1.0)

- Romanized Mandarin / Zhuyin sub-project (single pinyin standard; mind short
  syllables + collapse risk; keep a prefix code; see `cfbao/chinese-diceware`).
- Multilingual variants (ja/ko/zh) from the same pipeline.
- AnonTicket code-phrase integration: AnonTicket generates an identifier from
  six random dictionary words; this list could be its dictionary source.
  Confirm AnonTicket's expected wordlist format/length and license
  compatibility before wiring it in.

---

## 12. Caveats carried into implementation

- ✅ RESOLVED (T2, 2026-06-24): dictionary backing is no longer just "claimed" —
  all 160 pins were verified per-word against live OED/MW/Cambridge entries and
  flagged `verified` in `loanwords_seed.csv`.
- ✅ Addressed: the OED "addition year" claims (Korean 2021-09 / 2024-12 batches)
  were re-checked against live entries during T2.
- `wla` is not yet installed/run (cargo absent here); the build uses the
  Python-side prune + audit (§6 option A). NOTE: the system `/usr/bin/tidy` is
  HTML Tidy, NOT sts10/tidy — do not use it. Confirm `wla` flags when run.
- Sandbox network is allowlisted; all source data is vendored into
  `data/sources/` (freq snapshot + badwords) for offline reproducibility.
- Pin set is kept well under 7776 (160) so assembly always has fill room.
