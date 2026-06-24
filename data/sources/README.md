# Vendored 資料來源 / Vendored data sources

> 中英雙語 / Bilingual（正體中文 + English）。

所有輸入都 vendored 在這裡，讓建構可離線重現（SPEC §4）。
All inputs are vendored here so the build is reproducible offline (SPEC §4).

| 檔案 / File | 內容 / What | 來源 / Provenance | 授權 / License |
|------|------|---------------------|--------------|
| `loanwords_seed.csv` | 策展的亞洲外來語＋決策 / curated Asian loanwords + decisions | 本專案 / this project | CC-BY-4.0（同 `output/`） |
| `freq_en.txt` | 頻率排序英文 token（排序輸入）/ frequency-ordered English tokens (ranking input) | `wordfreq` top_n_list('en', 60000)，預過濾 `^[a-z]{2,12}$` | `wordfreq` 為 Apache/MIT；此處僅作排序用，見下 |
| `badwords_en.txt` | 冒犯字過濾 / offensive-word filter | LDNOOBW（en）| CC-BY-4.0（LDNOOBW）|
| `quality_exclude.txt` | 同音／難拼排除 / homophones & hard-to-spell | 本專案策展 / this project (curated) | CC-BY-4.0 |
| `proper_nouns.txt` | 要剔除的小寫專有名詞 / lowercased proper nouns to drop | 本專案策展 / this project (curated) | CC-BY-4.0 |

## 關於 `freq_en.txt` 與授權 / On `freq_en.txt` and licensing

`wordfreq` 匯整了多個不同授權的語料。我們嚴格地把它當「排序輸入」使用：它只決定
常見英文字被「考慮納入」的先後順序。最後進入 `output/` 的字是常見英文詞彙
（以及已在英文中詞彙化的外來語），並非逐字複製任何單一受著作權保護的彙編。這讓
輸出可在 CC-BY-4.0 下發佈（見 `LICENSE-DATA`）。用 `scripts/gen_freq_snapshot.py`
重新產生。
`wordfreq` aggregates many corpora under various licenses. We use it strictly as
a *ranking input*: it decides the order in which common English words are
considered for inclusion. The words that end up in `output/` are common English
vocabulary (and loanwords now lexicalized in English), not a verbatim copy of any
single copyrighted compilation. This keeps the output publishable under CC-BY-4.0
(see `LICENSE-DATA`). Regenerate with `scripts/gen_freq_snapshot.py`.

## 關於 Rust 工具（`tidy` / `wla`）/ On the Rust tooling

SPEC §6 提到 `tidy` 與 `wla`（https://github.com/sts10）。本專案的剪枝以 Python
完成（`prune.py`，SPEC §6 option A），核心建構兩者都不需要。`scripts/audit.sh` 在
有安裝 `wla` 時會額外跑它。
SPEC §6 references `tidy` and `wla` (https://github.com/sts10). Pruning is done
in Python (`prune.py`, SPEC §6 option A) so the core build needs neither.
`scripts/audit.sh` will additionally run `wla` if it is installed.

> 警告 / WARNING：macOS 系統內建的 `/usr/bin/tidy` 是 HTML Tidy，完全是另一個工具，
> 不要把詞表丟給它處理。
> the macOS system binary `/usr/bin/tidy` is HTML Tidy, a completely different
> tool. Do not pipe the wordlist through it.
