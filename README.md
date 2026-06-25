# asian-diceware

[![CI](https://github.com/anoni-net/asian-diceware/actions/workflows/ci.yml/badge.svg)](https://github.com/anoni-net/asian-diceware/actions/workflows/ci.yml)

> This README is bilingual. The **English version comes first**; the
> **正體中文 (Traditional Chinese) version follows below the English**.

## English

A Diceware-style / Diceware-compatible English passphrase wordlist that blends
two sources:

- high-frequency, easy-to-spell English words familiar to English users in
  Taiwan and the wider Sinophone region (low memorization and typing burden), and
- dictionary-attested Asian loanwords already absorbed into English
  (`tofu`, `typhoon`, `ramen`, `kimchi`, `karaoke`, `tsunami`, `boba`, ...).

The goal is exactly **7,776 words (6^5)**, matching the security and usability
properties of the [EFF Large Wordlist](https://www.eff.org/dice) so it works as a
drop-in alternative. Six words give about 77.5 bits of entropy.

> "Diceware" is Arnold Reinhold's term. This project is Diceware-style /
> Diceware-compatible and builds on prior art by the EFF and Reinhold.

### Status

Pre-1.0 (currently v0.3.1). The build pipeline runs end to end; all acceptance
tests (S1–S8) pass and the external `wla` audit passes. 161 dictionary-verified
Asian loanwords are pinned, and the 7,776-word frequency fill has been
quality-hardened (proper nouns, acronyms, and junk removed). See
[`SPEC.md`](SPEC.md) §9–§10 for the remaining work toward v1.0.

### Quick start

```bash
uv venv && uv pip install -e ".[dev]"
./scripts/run_pipeline.sh 7776      # full list (5 dice); use 1296 for the v0.1 slice
.venv/bin/pytest                    # acceptance tests S1–S8
```

Outputs land in `output/`:

- `asian_diceware_7776.txt` — the wordlist, one word per line.
- `asian_diceware_7776_dice.txt` — `11111<TAB>word` dice-roll mapping
  (base-6, digits 1–6).

To make a passphrase: roll 5 dice, read the result as a five-digit number, look
it up in the dice file; repeat for 6 words (~77.5 bits). Or pick words with a
cryptographic RNG. Always use true randomness; never hand-pick.

### How it works

A six-stage pipeline (see [`SPEC.md`](SPEC.md) §5):

`collect → normalize → filter_quality → prune → assemble → validate`

The frequency ranking comes from a vendored snapshot
(`data/sources/freq_en.txt`) derived from
[`wordfreq`](https://github.com/rspeer/wordfreq); loanwords come from the
curated, dictionary-verified `data/sources/loanwords_seed.csv`. Pinned loanwords
are protected through pruning: prefix collisions drop the non-pinned side, and a
collision between two pinned words fails the build loudly (SPEC §5.1).

### Featured Asian loanwords

The list pins **161 dictionary-attested Asian loanwords** (verified in OED /
Merriam-Webster / Cambridge). A selection by origin:

- **Japanese (62)** — `sushi` `ramen` `tofu` `miso` `matcha` `bento` `karaoke`
  `karate` `judo` `ninja` `samurai` `kimono` `origami` `bonsai` `emoji` `manga`
  `anime` `tsunami` `zen` `umami` `haiku` `ikebana` `kaizen`.
- **Korean (25)** — `kimchi` `bibimbap` `bulgogi` `soju` `hangul` `taekwondo`
  `hallyu` `manhwa` `mukbang` `oppa` `aegyo` `daebak` (many entered the OED in
  its 2021 / 2024 K-culture batches).
- **Chinese / Mandarin (12)** — `typhoon` `oolong` `ginseng` `qigong` `kowtow`
  `sampan` `pinyin` `yin` `yang` `pekoe` `kaolin` `boba`.
- **Cantonese (6)** — `wok` `wonton` `hoisin` `kumquat` `loquat` `cheongsam`.
- **Hokkien / Min-nan (1)** — `ketchup` (yes, it traces back to Hokkien).
- **South Asian / Sanskrit (31)** — `yoga` `karma` `guru` `mantra` `nirvana`
  `avatar` `chakra` `mandala` `naan` `biryani` `masala` `ghee` `chutney`
  `cheetah` `mongoose` `bazaar` `bandanna` `khaki` `pundit`.
- **Other Asian — Malay / South & SE Asian (24)** — `bamboo` `gong` `curry`
  `mango` `durian` `satay` `batik` `sarong` `rattan` `tempeh` `orangutan`
  `gecko` `cockatoo` `pangolin` `shampoo` `bungalow` `jungle` `loot` `thug`.

**You may not realize these are Asian loanwords:** `tycoon`, `honcho`,
`ketchup`, `shampoo`, `bungalow`, `jungle`, `loot`, `thug`, `cushy`, `atoll`,
`gecko`, `cheetah`, `gong`, `avatar`, `guru`, `bazaar`, `dinghy`, `mongoose`.

**Taiwan / Sinophone flavor:** `oolong` (Taiwanese tea), `boba` (bubble tea,
which originated in Taiwan), `typhoon`, `ketchup` (Hokkien), `pinyin`.

The full curated set, with each word's language, dictionary, and notes, lives in
[`data/sources/loanwords_seed.csv`](data/sources/loanwords_seed.csv).

### Licensing

- Code (`src/`, `scripts/`, `tests/`): MIT — see [`LICENSE`](LICENSE).
- Wordlist data (`output/*`, `data/sources/loanwords_seed.csv`): CC-BY-4.0 — see
  [`LICENSE-DATA`](LICENSE-DATA).

The frequency snapshot is used as a ranking input only; the words themselves are
common English vocabulary, not a verbatim copy of a copyrighted compilation. See
[`data/sources/README.md`](data/sources/README.md) for source provenance.

---

## 正體中文

一份 Diceware 風格、與 EFF 相容的英文密語詞表，混合兩種來源：

- 在台灣與華語圈熟悉、好拼好記的高頻英文字（降低記憶與輸入負擔）。
- 已被英文吸收、有字典背書的亞洲外來語（`tofu`、`typhoon`、`ramen`、`kimchi`、`karaoke`、`tsunami`、`boba` 等）。

目標是恰好 **7,776 字（6^5）**，安全性與可用性對齊 [EFF Large Wordlist](https://www.eff.org/dice)，可當成直接替代品。六個字約 77.5 bits 的熵。

> 「Diceware」是 Arnold Reinhold 的用語。本專案是 Diceware 風格／相容，並在 EFF 與 Reinhold 的先前成果之上發展。

### 狀態

Pre-1.0（目前 v0.3.1）。建構 pipeline 端到端可跑，驗收測試 S1–S8 全過，wla 外部稽核通過。已 pin 入 161 個字典查證過的亞洲外來語，7,776 字的頻率填充也經過品質強化（移除專有名詞、縮寫、雜訊）。到 v1.0 的剩餘工作見 [`SPEC.md`](SPEC.md) §9–§10。

### 快速開始

```bash
uv venv && uv pip install -e ".[dev]"
./scripts/run_pipeline.sh 7776      # 完整詞表（5 顆骰），用 1296 跑 v0.1 切片
.venv/bin/pytest                    # 驗收測試 S1–S8
```

產物落在 `output/`：

- `asian_diceware_7776.txt`：詞表，一行一個字。
- `asian_diceware_7776_dice.txt`：`11111<TAB>word` 骰子對應（base-6，數字 1–6）。

產生密語：擲 5 顆骰，讀成五位數，去 dice 檔查那一行，重複 6 次得 6 個字（約 77.5 bits）。或用密碼學亂數抽。務必用真亂數，不要自己挑。

### 運作方式

六階段 pipeline（見 [`SPEC.md`](SPEC.md) §5）：

`collect → normalize → filter_quality → prune → assemble → validate`

頻率排序來自 vendored 快照（`data/sources/freq_en.txt`，源自 [`wordfreq`](https://github.com/rspeer/wordfreq)）。外來語來自人工策展、字典查證的 `data/sources/loanwords_seed.csv`。被 pin 的外來語在剪枝全程受保護：prefix 衝突時剔除非 pin 的一方，兩個 pin 互相衝突則讓建構明確失敗（SPEC §5.1）。

### 特色亞洲字詞

詞表 pin 入 **161 個有字典背書的亞洲外來語**（經 OED／Merriam-Webster／Cambridge 查證）。依語源舉例：

- **日語（62）**：`sushi` `ramen` `tofu` `miso` `matcha` `bento` `karaoke` `karate` `judo` `ninja` `samurai` `kimono` `origami` `bonsai` `emoji` `manga` `anime` `tsunami` `zen` `umami` `haiku` `ikebana` `kaizen`。
- **韓語（25）**：`kimchi` `bibimbap` `bulgogi` `soju` `hangul` `taekwondo` `hallyu` `manhwa` `mukbang` `oppa` `aegyo` `daebak`（不少是 OED 2021／2024 韓流批次新增）。
- **華語／Mandarin（12）**：`typhoon` `oolong` `ginseng` `qigong` `kowtow` `sampan` `pinyin` `yin` `yang` `pekoe` `kaolin` `boba`。
- **粵語（6）**：`wok` `wonton` `hoisin` `kumquat` `loquat` `cheongsam`。
- **閩南語／台語（1）**：`ketchup`（沒錯，源頭可追到閩南語）。
- **南亞／梵語（31）**：`yoga` `karma` `guru` `mantra` `nirvana` `avatar` `chakra` `mandala` `naan` `biryani` `masala` `ghee` `chutney` `cheetah` `mongoose` `bazaar` `bandanna` `khaki` `pundit`。
- **其他亞洲（馬來／南亞、東南亞等，24）**：`bamboo` `gong` `curry` `mango` `durian` `satay` `batik` `sarong` `rattan` `tempeh` `orangutan` `gecko` `cockatoo` `pangolin` `shampoo` `bungalow` `jungle` `loot` `thug`。

**你可能沒發現這些其實是亞洲外來語**：`tycoon`（大亨）、`honcho`（老大）、`ketchup`、`shampoo`、`bungalow`、`jungle`、`loot`、`thug`、`cushy`、`atoll`、`gecko`、`cheetah`、`gong`、`avatar`、`guru`、`bazaar`、`dinghy`、`mongoose`。

**台灣／華語圈味**：`oolong`（烏龍茶）、`boba`（珍珠奶茶，源自台灣）、`typhoon`（颱風）、`ketchup`（閩南語）、`pinyin`（拼音）。

完整清單（含每字語源、字典、備註）在 [`data/sources/loanwords_seed.csv`](data/sources/loanwords_seed.csv)。

### 授權

- 程式碼（`src/`、`scripts/`、`tests/`）：MIT，見 [`LICENSE`](LICENSE)。
- 詞表資料（`output/*`、`data/sources/loanwords_seed.csv`）：CC-BY-4.0，見 [`LICENSE-DATA`](LICENSE-DATA)。

頻率快照僅作為排序輸入。詞表裡的字是常見英文詞彙，並非逐字複製受著作權保護的彙編。來源出處見 [`data/sources/README.md`](data/sources/README.md)。
