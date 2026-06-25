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

### Choosing a list: 7776 vs 1296

Both files come out of the same pipeline, so they share the same words; they
differ only in how many.

| List | Words | Dice/word | Bits/word | 6 words | Best for |
|---|---|---|---|---|---|
| `7776` | 7,776 (6⁵) | 5 | 12.925 | ~77.5 bits | Real passphrases — EFF-compatible drop-in (**default**) |
| `1296` | 1,296 (6⁴) | 4 | 10.340 | ~62.0 bits | Tests / demos / teaching; 4-dice simplicity; a shorter card to print |

- **Same recipe.** Each list is the 161 pinned loanwords plus the
  highest-frequency fill. Every word in `1296` is also in `7776` — the small
  list just stops sooner (a strict subset).
- **Use `7776` for anything real.** It reaches the EFF strength target (6 words
  ≈ 77.5 bits) and needs only 5 dice per word.
- **`1296` trades entropy for size.** Only 4 dice and a shorter list to print or
  eyeball, at the cost of more words per passphrase: it takes about 8 words from
  `1296` to match 6 words from `7776`. Handy for tests, demos, and teaching the
  method.
- **Dice codes are per file.** The same word gets a different roll in each,
  because each file is numbered within its own alphabetical order: `tofu` is
  `6336` in the 1296 dice file but `63444` in the 7776 one. Always read the dice
  file that matches the list you picked.

### Making a passphrase

**1. With physical dice (`7776`).** Roll 5 dice, read them left to right as a
five-digit number (each die 1–6), and find that code in
`asian_diceware_7776_dice.txt`. Repeat for 6 words and join them with `-`. For
example, the rolls `6 3 4 4 4 → 63444` map to `tofu`; six such rolls give about
77.5 bits.

**2. In Python (no dice, cryptographically secure).**

```python
import secrets

words = open("output/asian_diceware_7776.txt").read().split()
assert len(words) == 7776
phrase = "-".join(secrets.choice(words) for _ in range(6))
print(phrase)        # ~77.5 bits, e.g. tofu-ramen-bazaar-oolong-gecko-haiku
```

Use `secrets` (a cryptographically secure RNG), never `random`, for passphrases.

**3. The quick CLI way.** A portable one-liner (macOS + Linux, still a
secure RNG):

```bash
python3 -c "import secrets;w=open('output/asian_diceware_7776.txt').read().split();print('-'.join(secrets.choice(w) for _ in range(6)))"
```

Drop a helper in `~/.zshrc` (the argument is the word count; pipe to `pbcopy` to
copy on macOS):

```bash
asianpass() { python3 -c "import secrets;w=open('$HOME/asian-diceware/output/asian_diceware_7776.txt').read().split();print('-'.join(secrets.choice(w) for _ in range(${1:-6})))"; }
# asianpass            -> 6 words
# asianpass 8 | pbcopy -> 8 words, copied to the clipboard
```

No clone needed — pull the published list straight from GitHub:

```bash
curl -s https://raw.githubusercontent.com/anoni-net/asian-diceware/main/output/asian_diceware_7776.txt \
  | python3 -c "import secrets,sys;w=sys.stdin.read().split();print('-'.join(secrets.choice(w) for _ in range(6)))"
```

On Linux you can also use `shuf` with a secure source:
`shuf -n6 --random-source=/dev/urandom output/asian_diceware_7776.txt | paste -sd- -`
(stock macOS has no `shuf`; `brew install coreutils` gives you `gshuf`).

Append a digit or symbol if a site demands one. Want more strength? Add words:
each extra `7776` word is worth about 12.9 more bits.

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

### 該用哪一份：7776 還是 1296

兩個檔案由同一條 pipeline 產生，用字相同，差別只在數量。

| 詞表 | 字數 | 每字骰數 | 每字 bits | 六字 | 適合 |
|---|---|---|---|---|---|
| `7776` | 7,776（6⁵） | 5 | 12.925 | 約 77.5 bits | 正式密語，EFF 相容的直接替代品（**預設**）|
| `1296` | 1,296（6⁴） | 4 | 10.340 | 約 62.0 bits | 測試、示範、教學。只要 4 顆骰，清單較短好印 |

- **同一套配方**。每份都是 161 個 pin 的外來語，加上最高頻的填充字。`1296` 裡的每個字也都在 `7776` 裡，小表只是提早收尾，是 `7776` 的子集。
- **正式使用就用 `7776`**。它達到 EFF 的強度目標（六字約 77.5 bits），每字只要 5 顆骰。
- **`1296` 用熵換體積**。只要 4 顆骰、清單較短好印好看，代價是每組密語要更多字。用 `1296` 大約要 8 個字，才追得上 `7776` 的 6 個字。適合測試、示範、教學。
- **骰子代碼各檔不同**。同一個字在兩份檔案的代碼不一樣，因為每份依各自的字母順序編號：`tofu` 在 1296 的骰子檔是 `6336`，在 7776 是 `63444`。查表時一定要對到你選的那一份骰子檔。

### 怎麼用這份表

**1. 用實體骰子（`7776`）**。擲 5 顆骰，由左到右讀成五位數（每顆 1–6），到 `asian_diceware_7776_dice.txt` 找那一行。重複 6 次，用 `-` 串起來。例如擲出 `6 3 4 4 4 → 63444` 對到 `tofu`，六次這樣的擲骰約 77.5 bits。

**2. 用 Python（不靠骰子，且密碼學安全）**。

```python
import secrets

words = open("output/asian_diceware_7776.txt").read().split()
assert len(words) == 7776
phrase = "-".join(secrets.choice(words) for _ in range(6))
print(phrase)        # 約 77.5 bits，例如 tofu-ramen-bazaar-oolong-gecko-haiku
```

產密語請用 `secrets`（密碼學安全的亂數），不要用 `random`。

**3. 工程師的快捷用法**。可跨平台的一行指令（macOS 與 Linux 都行，一樣用安全亂數）：

```bash
python3 -c "import secrets;w=open('output/asian_diceware_7776.txt').read().split();print('-'.join(secrets.choice(w) for _ in range(6)))"
```

在 `~/.zshrc` 放個小函式（參數是字數，macOS 可接 `pbcopy` 複製）：

```bash
asianpass() { python3 -c "import secrets;w=open('$HOME/asian-diceware/output/asian_diceware_7776.txt').read().split();print('-'.join(secrets.choice(w) for _ in range(${1:-6})))"; }
# asianpass            -> 6 個字
# asianpass 8 | pbcopy -> 8 個字，複製到剪貼簿
```

不想 clone 也行，直接從 GitHub 抓已發布的清單：

```bash
curl -s https://raw.githubusercontent.com/anoni-net/asian-diceware/main/output/asian_diceware_7776.txt \
  | python3 -c "import secrets,sys;w=sys.stdin.read().split();print('-'.join(secrets.choice(w) for _ in range(6)))"
```

Linux 也可以用 `shuf` 搭配安全的亂數來源：
`shuf -n6 --random-source=/dev/urandom output/asian_diceware_7776.txt | paste -sd- -`
（macOS 內建沒有 `shuf`，`brew install coreutils` 後可用 `gshuf`）。

網站若硬要數字或符號，補一個上去就好。想更強就加字：每多一個 `7776` 的字約多 12.9 bits。

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
