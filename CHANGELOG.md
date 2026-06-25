# 變更紀錄 / Changelog

> 中英雙語 / Bilingual（正體中文 + English）。

格式參考 [Keep a Changelog](https://keepachangelog.com/)，到 v1.0 後採語意化版號。
The format follows [Keep a Changelog](https://keepachangelog.com/), and the
project aims to follow semantic versioning once it reaches v1.0.

## [0.4.0] — 2026-06-25

### 變更 / Changed
- **亞洲外來語 pin 擴充 161 → 292（約 7776 的 3.8%）/ Asian-loanword pin expansion
  161 → 292 (~3.8% of 7776).** 把亞洲特色字的占比往 4% 拉。新詞由分語言的 agent
  策展、逐字以 MW／Cambridge／OED 線上查證：日語 +28、南亞 +37、韓語 +5、馬來／東南亞
  +13、粵語 +1，另把 24 個複查存活的 `hold` 升為 pin。每個新詞都過同一關（單一字典
  token、`[a-z]{3,9}`、prefix-free、無羅馬拼音強變體、非同音、非冒犯）。
  Agent-sourced, per-word web-verified expansion across Japanese, South Asian,
  Korean, Malay/SE-Asian, and Chinese, plus 24 re-verified holds promoted.
- **辨識度優先 / Recognizability-first.** 拉到剛好 4%（311）需納入台灣／華語圈不認得
  的冷僻詞（殖民時期詞彙、度量衡、罕見動物）。選擇辨識度而非剛好的百分比：pin 入
  可辨識的詞（食物、文化、瑜伽、樂器），誠實落在 292，把冷僻但有字典背書的詞留作
  `loanwords_seed.csv` 的 `decision=hold`（日後可再升）。pin 占比不影響密碼熵
  （12.925 bits/字來自 count=7776＋均勻抽樣＋prefix-free，與詞源無關），只改變辨識度。
  Hitting a round 4% would require obscure words a Taiwan/Sinophone reader would
  not recognize, so we kept the obscure-but-verified tail as `hold` and landed
  honestly at 292. Pin share does not affect passphrase entropy.
- `validate.py` 的諮詢帶 `PIN_BAND` 由 `(120,180)` 調為 `(250,350)`；版號升至 `0.4.0`。
  Advisory `PIN_BAND` raised to `(250,350)`; version bumped to `0.4.0`.

### 新增 / Added
- **可列印小冊 / Printable booklet**（`scripts/make_booklet.py`）：用 weasyprint + segno
  把 7776 詞表排成 A5/A6 擲骰查表小冊，含封面、使用教學、QR、CC-BY 版權頁，輸出到
  `output/`（gitignored）。以可嵌入的開源字型（Noto Sans TC、JetBrains Mono）內嵌中文，
  任何 PDF 看圖程式都顯示得出來。新增 `[booklet]` optional 套件與 `scripts/make_booklet.sh` 封裝，
  README 補「印成小冊」說明。
  A printable booklet generator (weasyprint + segno) that lays the 7776 list
  out as an A5/A6 roll-lookup booklet with a cover, how-to, QR, and a CC-BY
  colophon, written to `output/` (gitignored). Embeds open fonts (Noto Sans TC +
  JetBrains Mono) so Chinese renders in any viewer. Adds a `[booklet]` extra and the
  `scripts/make_booklet.sh` wrapper; README gains a "Print a booklet" section.
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
  以及「如何使用這份表」教學（實體骰子、Python 的 `secrets` 範例、命令列快捷用法）與「其他用途」（兩人暗號、把號碼唸成字）。
  Added a README section comparing the 7776 and 1296 lists (when to use each)
  and a "Making a passphrase" tutorial: physical dice, a Python `secrets`
  example, quick command-line one-liners, and an "Other uses" note (a two-person recognition phrase, and reading numbers aloud as words).
- **README 補充 / README additions**：新增「為什麼只有 ~3.8%」說明（啤酒 ABV 比喻），
  並把正體中文段落改為書面語。
  Added a "Why ~3.8%?" section (beer-ABV framing) and formalized the zh-TW register.

### 排除 / Excluded
- 複查後排除 13 個原 `hold`：`sake`（與英文 for the sake of 同形）、`banzai`／`noh`、
  `tao`／`ginkgo`／`pakchoi`／`taipan` 等羅馬拼音變體或同形衝突、`amok`（綁在片語 run amok）、
  以及 `tonkatsu`／`tonkotsu`／`donburi`／`senpai`／`yukata`（非 MW／Cambridge 詞條）。
  Re-verification excluded 13 former holds on homograph, romanization-variant,
  phrase-bound, or non-headword grounds.

## [0.3.1] — 2026-06-25

### 變更 / Changed
- `boba`（波霸/珍奶，台灣發源）由 `hold` 升為 `pin`，補強台灣味；pin 數 160 → 161。
  Promote `boba` (bubble tea, originated in Taiwan) from `hold` to a pin; 160 → 161 pins.

## [0.3.0] — 2026-06-25

### 變更 / Changed
- **v0.3 品質強化 / Quality hardening of the 7776 fill**：以多輪 agent ＋ 人工審閱，
  從頻率填充字中移除約 2,600 個專有名詞、縮寫、slang、非英文 token，並以乾淨字遞補；
  最終 7776 每字皆經審閱、0 縮寫；`wla` 外部稽核通過。過濾清單擴充至
  `proper_nouns.txt` ≈ 2,238、`quality_exclude.txt` ≈ 544。
  Removed ~2,600 proper nouns / acronyms / slang / foreign tokens from the
  frequency fill across a multi-round review and refilled with clean words; every
  final word reviewed; the `wla` external audit passes.

## [0.2.0] — 2026-06-24

### 新增 / Added
- **外來語種子擴充（`loanwords_seed.csv` 的 v0.2 區段）/ Loanword seed expansion**：
  +71 個 pin → **160 個 pin 外來語**（落在 SPEC §3.9 的 120–180 目標帶），
  經字典查證（OED/MW/Cambridge），語言分布均衡且 prefix-free 安全。另外 48 個候選
  以 `hold` 暫存供 T2 審查（中信心、超過上限、或 prefix 衝突落敗方，例如 `tea`
  因與 `teak` 衝突而暫存）。
  +71 pins → 160 pinned loanwords (within the 120–180 target), dictionary-
  verified, balanced across languages and prefix-free-safe; 48 more parked as
  `hold` for T2.
- **T2 完成 / Loanword verification (T2)**：原始 89 個 pin 全部逐字對
  OED/MW/Cambridge 的「實際條目」查證通過（無一需改拼法或降級），解除 SPEC §12
  的「字典背書未驗證」caveat。全部 160 個 pin 的 `dict` 改記實際查到的字典、
  `flags` 標注 `verified`，並補上 headword 細節（如 `kimchi`／`ketchup` 為
  MW headword，`kimchee`／`catsup` 為變體；`veranda` 為主 headword）。
  All 89 original pins verified against live OED/MW/Cambridge entries (none needed
  spelling changes or demotion); the full 160-pin set is now dictionary-verified
  and frozen.

## [0.1.0] — 2026-06-24

### 新增 / Added
- 專案骨架 / Repo skeleton：`pyproject.toml`（ruff + pytest）、MIT `LICENSE`、
  CC-BY-4.0 `LICENSE-DATA`、`CONTRIBUTING.md`。
- 六階段建構 pipeline / Six-stage build pipeline（`collect`、`normalize`、
  `filter_quality`、`prune`、`assemble`、`validate`），由 `asian_diceware.cli` 串接。
- Python 端的 prefix-free 剪枝，搭配受保護的 pin 集合（SPEC §5.1 option A）；
  pin↔pin 衝突會明確失敗。
  Python-side prefix-free pruning with a protected pin set (SPEC §5.1 option A);
  fails loudly on a pinned↔pinned collision.
- 初始外來語種子（`loanwords_seed.csv`）/ Initial loanword seed.
- Vendored 資料來源 / Vendored data sources：`freq_en.txt`（wordfreq 快照）、
  `badwords_en.txt`。
- 驗收測試 S1–S8（`tests/test_wordlist.py`）＋ pipeline 行為測試
  （`tests/test_pipeline.py`）。
- `scripts/run_pipeline.sh`、`scripts/audit.sh`、`scripts/gen_freq_snapshot.py`。

### 里程碑 / Milestone
- pipeline 端到端跑出一份 1296 字（4 顆骰）詞表，全部驗收測試通過，證明方法論可行。
  pipeline runs end to end producing a 1296-word (4-dice) list with all
  acceptance tests green — proves the methodology.
