# asian-diceware

> 中英雙語文件 / Bilingual (正體中文 + English)。中文在前，英文在後。
> Chinese first, English second in each section.

一份 Diceware 風格、與 EFF 相容的英文密語詞表，混合兩種來源：

- 在台灣與華語圈熟悉、好拼好記的高頻英文字（降低記憶與輸入負擔），以及
- 已被英文吸收、有字典背書的亞洲外來語（`tofu`、`typhoon`、`ramen`、`kimchi`、`karaoke`、`tsunami` 等）。

A Diceware-style, EFF-compatible English passphrase wordlist that blends two
sources:

- high-frequency, easy-to-spell English words familiar in Taiwan and the wider
  Sinophone region (low memorization and typing burden), and
- dictionary-attested Asian loanwords already absorbed into English.

目標是一份恰好 **7,776 字（6^5）** 的詞表，安全性與可用性對齊
[EFF Large Wordlist](https://www.eff.org/dice)，可當成直接替代品。六個字約
77.5 bits 的熵。

The goal is exactly **7,776 words (6^5)**, matching the security and usability
properties of the EFF Large Wordlist so it works as a drop-in alternative. Six
words give about 77.5 bits of entropy.

> 「Diceware」是 Arnold Reinhold 的用語。本專案是 **Diceware 風格／相容**，
> 並在 EFF 與 Reinhold 的先前成果之上發展。
>
> "Diceware" is Arnold Reinhold's term. This project is **Diceware-style /
> Diceware-compatible** and builds on prior art by the EFF and Reinhold.

## 狀態 / Status

Pre-1.0。建構 pipeline 已端到端跑通，在縮小目標（v0.1，1296 字／4 顆骰）下
全部驗收測試通過，用以驗證方法論。放大到完整 7,776 字、以及外來語策展收尾
記錄在 [`SPEC.md`](SPEC.md) §9–§10。

Pre-1.0. The build pipeline runs end to end and all acceptance tests pass at a
reduced target (v0.1, 1296 words / 4 dice) to prove the methodology. Scaling to
the full 7,776-word list and finalizing loanword curation are tracked in
[`SPEC.md`](SPEC.md) §9–§10.

## 快速開始 / Quick start

```bash
uv venv && uv pip install -e ".[dev]"

# 端到端建一份詞表（預設目標 7776；用 1296 跑 v0.1 切片）
# Build a wordlist end to end (default target 7776; use 1296 for the v0.1 slice):
./scripts/run_pipeline.sh 1296

# 或用 CLI / Or via the CLI:
.venv/bin/asian-diceware all --target 1296

# 跑驗收測試 / Run the acceptance tests (S1–S8):
.venv/bin/pytest
```

產物落在 `output/` / Outputs land in `output/`:

- `asian_diceware_<N>.txt` — 一行一個字 / one word per line.
- `asian_diceware_<N>_dice.txt` — `11111<TAB>word` 骰子對應（base-6，數字 1–6）
  / dice-roll mapping (base-6, digits 1–6).

## 運作方式 / How it works

六階段 pipeline（見 [`SPEC.md`](SPEC.md) §5）/ A six-stage pipeline:

`collect → normalize → filter_quality → prune → assemble → validate`

頻率排序來自 vendored 快照（`data/sources/freq_en.txt`，源自
[`wordfreq`](https://github.com/rspeer/wordfreq)）；外來語來自
`data/sources/loanwords_seed.csv`。被 pin 的外來語在剪枝全程受保護：prefix 衝突
時剔除非 pin 的一方，兩個 pin 互相衝突則讓建構明確失敗（SPEC §5.1）。

The frequency ranking comes from a vendored snapshot
(`data/sources/freq_en.txt`) derived from `wordfreq`; loanwords come from
`data/sources/loanwords_seed.csv`. Pinned loanwords are protected through
pruning: prefix collisions drop the non-pinned side, and a collision between two
pinned words fails the build loudly (SPEC §5.1).

## 授權 / Licensing

- **程式碼 / Code** (`src/`, `scripts/`, `tests/`): MIT，見 [`LICENSE`](LICENSE)。
- **詞表資料 / Wordlist data** (`output/*`, `data/sources/loanwords_seed.csv`):
  CC-BY-4.0，見 [`LICENSE-DATA`](LICENSE-DATA)。

頻率快照僅作為「排序輸入」使用；詞表裡的字是常見英文詞彙，並非逐字複製某份
受著作權保護的彙編。來源出處見 [`data/sources/README.md`](data/sources/README.md)。

The frequency snapshot is used only as a ranking input; the words themselves are
common English vocabulary, not a verbatim copy of a copyrighted compilation. See
`data/sources/README.md` for source provenance.
