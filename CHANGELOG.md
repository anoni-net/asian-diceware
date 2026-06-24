# 變更紀錄 / Changelog

> 中英雙語 / Bilingual（正體中文 + English）。

格式參考 [Keep a Changelog](https://keepachangelog.com/)，到 v1.0 後採語意化版號。
The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project aims to follow semantic versioning once it reaches v1.0.

## [Unreleased]

### 新增 / Added
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

### 里程碑 / Milestone
- **v0.1**：pipeline 端到端跑出一份 1296 字（4 顆骰）詞表，全部驗收測試通過，
  證明方法論可行。
  pipeline runs end to end producing a 1296-word (4-dice) list with all
  acceptance tests green — proves the methodology.
