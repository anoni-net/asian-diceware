# 貢獻指南 / Contributing

> 中英雙語 / Bilingual（正體中文 + English）。

## 外來語策展 / Loanword curation

外來語的單一事實來源是 `data/sources/loanwords_seed.csv`。每一列欄位為：
`word, lang, length, dict, flags, decision, notes`。
The single source of truth for loanwords is `data/sources/loanwords_seed.csv`.
Each row has: `word, lang, length, dict, flags, decision, notes`.

`decision` 三選一 / `decision` is one of:

- `pin` — 強制納入最終詞表，剪枝時受保護。
  force this word into the final list; protected from pruning.
- `hold` — 審查中的候選，尚未納入。
  candidate under review; not yet included.
- `exclude` — 已否決（保留該列供追溯，理由寫在 `notes`）。
  rejected (keep the row for traceability + the reason in `notes`).

一個字要能被 `pin`，必須滿足 / Rules for a word to be eligible for `pin`:

1. 單一 token：無空白、無連字號、無撇號。
   Single token: no space, no hyphen, no apostrophe.
2. 符合 `^[a-z]{3,9}$`（3–9 個小寫 ASCII 字母）。
   Matches `^[a-z]{3,9}$` (3–9 lowercase ASCII letters).
3. 有真實字典條目（OED / Merriam-Webster / Cambridge），把來源記在 `dict` 欄。
   **務必查證實際條目，不要只信「某年新增」的文章。**
   Has a real dictionary entry (OED / Merriam-Webster / Cambridge). Record which
   in the `dict` column. **Verify the live entry — do not trust an "added in
   year X" article.**
4. 非冒犯／歧視／敏感字，非專有名詞（已詞彙化為常見名詞的外來語可以）。
   Not offensive/slur/sensitive. Not a proper noun (loanwords lexicalized as
   common nouns are fine).
5. 沒有相互競爭的主流羅馬拼音（我們不自行音譯國語，只接受字典已定型的拼法）。
   No dominant competing romanization (we never transliterate Mandarin
   ourselves; only accept dictionary-fixed spellings).

改動種子清單後，重跑 pipeline 與測試 / When you change the seed list, re-run the
pipeline and the tests:

```bash
./scripts/run_pipeline.sh 7776 && .venv/bin/pytest
```

## 程式碼 / Code

- 用 `ruff` 格式化／檢查 / Format / lint with `ruff`: `ruff check . && ruff format .`
- 測試必須維持綠燈 / Tests must stay green: `pytest`.
- `prune.py` 的 pin/prune 優先序是最棘手的不變量，見 `SPEC.md` §5.1。pin↔pin 的
  prefix 衝突必須讓建構明確失敗，絕不可默默丟掉一個 pin。
  The pin/prune precedence in `prune.py` is the trickiest invariant — see
  `SPEC.md` §5.1. A pinned↔pinned prefix collision must fail the build loudly,
  never silently drop a pinned word.

## 重新產生頻率快照 / Regenerating the frequency snapshot

`data/sources/freq_en.txt` 為了離線、可重現的建構而 vendored。要重新產生
（需要 `snapshot` extra）/ It is vendored for offline, reproducible builds. To
regenerate it (requires the `snapshot` extra):

```bash
uv pip install -e ".[snapshot]"
.venv/bin/python scripts/gen_freq_snapshot.py
```

## 提交慣例 / Commit conventions

- 身分用 / Identity: `Toomore Chiang (anoni.net) <toomore@anoni.net>`，並以 PGP
  簽章（`commit.gpgsign = true`）/ with PGP signing.
- Commit 訊息採中英雙語：主旨一行，內文中英對照。
  Commit messages are bilingual: a single-line subject, with zh-TW and English
  in the body.
