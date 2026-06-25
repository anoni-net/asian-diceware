# 變更紀錄 / Changelog

> 中英雙語 / Bilingual（正體中文 + English）。

格式參考 [Keep a Changelog](https://keepachangelog.com/)，到 v1.0 後採語意化版號。
The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project aims to follow semantic versioning once it reaches v1.0.

## [Unreleased]

### 新增 / Added
- **CI 驗證 / Continuous integration**（`.github/workflows/ci.yml`）：
  - `lint-test`：ruff（lint + format）與 pytest，在 Python 3.11/3.12/3.13 上跑。
  - `reproducibility`：從 vendored 來源重建 1296、7776 詞表，以 `git diff --exit-code`
    確認與 commit 的清單逐位元相符，並跑 S1–S8 稽核。
  - `external-audit`：用 Rust 的 `wla`（Word List Auditor）做外部稽核（binary 有 cache）。
  README 加上 CI 狀態徽章。
  GitHub Actions CI with three jobs: ruff + pytest matrix (3.11/3.12/3.13); a
  reproducibility gate (rebuild from vendored sources must byte-match the
  committed lists + S1–S8); and the `wla` external audit (binary cached). Added
  a CI status badge to the README.
- **使用教學 / Usage guide**（README）：新增「7776 vs 1296 該用哪一份」比較表，
  以及「怎麼用這份表」教學（實體骰子、Python 的 `secrets` 範例、命令列快捷用法）。
  Added a README section comparing the 7776 and 1296 lists (when to use each)
  and a "Making a passphrase" tutorial: physical dice, a Python `secrets`
  example, and quick command-line one-liners.
- 專案骨架 / Repo skeleton：`pyproject.toml`（ruff + pytest）、MIT `LICENSE`、
  CC-BY-4.0 `LICENSE-DATA`、`CONTRIBUTING.md`。
- 六階段建構 pipeline / Six-stage build pipeline（`collect`、`normalize`、
  `filter_quality`、`prune`、`assemble`、`validate`），由 `asian_diceware.cli` 串接。
- Python 端的 prefix-free 剪枝，搭配受保護的 pin 集合（SPEC §5.1 option A）；
  pin↔pin 衝突會明確失敗。
  Python-side prefix-free pruning with a protected pin set (SPEC §5.1 option A);
  fails loudly on a pinned↔pinned collision.
- Vendored 資料來源 / Vendored data sources：`freq_en.txt`（wordfreq 快照）、
  `badwords_en.txt`。
- **外來語種子擴充（`loanwords_seed.csv` 的 v0.2 區段）/ Loanword seed expansion**：
  +71 個 pin → **160 個 pin 外來語**（落在 SPEC §3.9 的 120–180 目標帶），
  經字典查證（OED/MW/Cambridge），語言分布均衡且 prefix-free 安全。另外 48 個候選
  以 `hold` 暫存供 T2 審查（中信心、超過上限、或 prefix 衝突落敗方，例如 `tea`
  因與 `teak` 衝突而暫存）。
  +71 pins → 160 pinned loanwords (within the 120–180 target), dictionary-
  verified, balanced across languages and prefix-free-safe; 48 more parked as
  `hold` for T2.
- 驗收測試 S1–S8（`tests/test_wordlist.py`）＋ pipeline 行為測試
  （`tests/test_pipeline.py`）。
- `scripts/run_pipeline.sh`、`scripts/audit.sh`、`scripts/gen_freq_snapshot.py`。
- **T2 完成 / Loanword verification (T2)**：原始 89 個 pin 全部逐字對
  OED/MW/Cambridge 的「實際條目」查證通過（無一需改拼法或降級），解除 SPEC §12
  的「字典背書未驗證」caveat。全部 160 個 pin 的 `dict` 改記實際查到的字典、
  `flags` 標注 `verified`，並補上 headword 細節（如 `kimchi`／`ketchup` 為
  MW headword，`kimchee`／`catsup` 為變體；`veranda` 為主 headword）。
  All 89 original pins verified against live OED/MW/Cambridge entries (none needed
  spelling changes or demotion); the full 160-pin set is now dictionary-verified
  and frozen.
- **v0.3 品質強化 / Quality hardening of the 7776 fill**：以多輪 agent ＋ 人工審閱，
  從頻率填充字中移除約 2,600 個專有名詞、縮寫、slang、非英文 token，並以乾淨字遞補；
  最終 7776 每字皆經審閱、0 縮寫；`wla` 外部稽核通過。過濾清單擴充至
  `proper_nouns.txt` ≈ 2,238、`quality_exclude.txt` ≈ 544。
  Removed ~2,600 proper nouns / acronyms / slang / foreign tokens from the
  frequency fill across a multi-round review and refilled with clean words; every
  final word reviewed; the `wla` external audit passes.

### 里程碑 / Milestone
- **v0.1**：pipeline 端到端跑出一份 1296 字（4 顆骰）詞表，全部驗收測試通過，
  證明方法論可行。
  pipeline runs end to end producing a 1296-word (4-dice) list with all
  acceptance tests green — proves the methodology.
- **v0.2**：外來語策展完成、pin 集凍結（160 個皆字典查證）。
  loanword curation done (T2); the 160-pin set is frozen and dictionary-verified.
- **v0.3**：7776 詞表品質強化（移除約 2,600 雜訊字、`wla` 稽核通過）。
  fill quality-hardened (~2,600 junk words removed; `wla` audit passes).
- **v0.3.1**：`boba`（波霸/珍奶，台灣發源）升為 pin，補強台灣味；pin 數 160 → 161。
  promote `boba` (bubble tea, originated in Taiwan) to a pin; 160 → 161 pins.
