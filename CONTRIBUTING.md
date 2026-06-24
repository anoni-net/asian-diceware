# Contributing

> This document is bilingual. The **English version comes first**; the
> **正體中文 (Traditional Chinese) version follows below the English**.

## English

### Loanword curation

The single source of truth for loanwords is `data/sources/loanwords_seed.csv`.
Each row has: `word, lang, length, dict, flags, decision, notes`.

`decision` is one of:

- `pin` — force this word into the final list; protected from pruning.
- `hold` — candidate under review; not yet included.
- `exclude` — rejected (keep the row for traceability + the reason in `notes`).

Rules for a word to be eligible for `pin`:

1. Single token: no space, no hyphen, no apostrophe.
2. Matches `^[a-z]{3,9}$` (3–9 lowercase ASCII letters).
3. Has a real dictionary entry (OED / Merriam-Webster / Cambridge). Record which
   in the `dict` column. **Verify the live entry — do not trust an "added in
   year X" article.**
4. Not offensive/slur/sensitive. Not a proper noun (loanwords lexicalized as
   common nouns are fine).
5. No dominant competing romanization (we never transliterate Mandarin
   ourselves; only accept dictionary-fixed spellings).

When you change the seed list, re-run the pipeline and the tests:

```bash
./scripts/run_pipeline.sh 7776 && .venv/bin/pytest
```

### Code

- Format / lint with `ruff`: `ruff check . && ruff format .`
- Tests must stay green: `pytest`.
- The pin/prune precedence in `prune.py` is the trickiest invariant — see
  `SPEC.md` §5.1. A pinned↔pinned prefix collision must fail the build loudly,
  never silently drop a pinned word.

### Regenerating the frequency snapshot

`data/sources/freq_en.txt` is vendored for offline, reproducible builds. To
regenerate it (requires the `snapshot` extra):

```bash
uv pip install -e ".[snapshot]"
.venv/bin/python scripts/gen_freq_snapshot.py
```

### Commit conventions

- Identity: `Toomore Chiang (anoni.net) <toomore@anoni.net>`, with PGP signing
  (`commit.gpgsign = true`).
- Commit messages are bilingual: a single-line subject, with zh-TW and English
  in the body.

---

## 正體中文

### 外來語策展

外來語的單一事實來源是 `data/sources/loanwords_seed.csv`。每一列欄位為：
`word, lang, length, dict, flags, decision, notes`。

`decision` 三選一：

- `pin`：強制納入最終詞表，剪枝時受保護。
- `hold`：審查中的候選，尚未納入。
- `exclude`：已否決（保留該列供追溯，理由寫在 `notes`）。

一個字要能被 `pin`，必須滿足：

1. 單一 token：無空白、無連字號、無撇號。
2. 符合 `^[a-z]{3,9}$`（3–9 個小寫 ASCII 字母）。
3. 有真實字典條目（OED / Merriam-Webster / Cambridge），把來源記在 `dict` 欄。
   務必查證實際條目，不要只信「某年新增」的文章。
4. 非冒犯／歧視／敏感字，非專有名詞（已詞彙化為常見名詞的外來語可以）。
5. 沒有相互競爭的主流羅馬拼音（我們不自行音譯國語，只接受字典已定型的拼法）。

改動種子清單後，重跑 pipeline 與測試：

```bash
./scripts/run_pipeline.sh 7776 && .venv/bin/pytest
```

### 程式碼

- 用 `ruff` 格式化／檢查：`ruff check . && ruff format .`
- 測試必須維持綠燈：`pytest`。
- `prune.py` 的 pin/prune 優先序是最棘手的不變量，見 `SPEC.md` §5.1。pin↔pin 的 prefix 衝突必須讓建構明確失敗，絕不可默默丟掉一個 pin。

### 重新產生頻率快照

`data/sources/freq_en.txt` 為了離線、可重現的建構而 vendored。要重新產生（需要 `snapshot` extra）：

```bash
uv pip install -e ".[snapshot]"
.venv/bin/python scripts/gen_freq_snapshot.py
```

### 提交慣例

- 身分用：`Toomore Chiang (anoni.net) <toomore@anoni.net>`，並以 PGP 簽章（`commit.gpgsign = true`）。
- Commit 訊息採中英雙語：主旨一行，內文中英對照。
