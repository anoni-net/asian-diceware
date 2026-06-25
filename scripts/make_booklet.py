#!/usr/bin/env python3
"""產生可列印的查表小冊（PDF）。/ Generate a printable lookup booklet (PDF).

讀 output/asian_diceware_<target>_dice.txt（已是擲骰順序），用 weasyprint 排成
A5/A6 多欄查表，再加上封面、使用教學、版權頁，輸出到 output/。
Reads the roll-ordered dice file and lays it out with weasyprint into an A5/A6
multi-column lookup table, with a cover, a how-to page, and a colophon.

中文字型 / CJK fonts：為了讓中文在任何看圖程式都顯示得出來，本工具會把可嵌入的
開源字型（Noto Sans TC，思源黑體同源）實例成靜態 Regular/Bold 後用 @font-face 內嵌，
避免使用不可轉散布的系統字型（PingFang 等）。macOS 安裝：
    brew install --cask font-noto-sans-tc
To make sure Chinese shows everywhere, this tool instances an embeddable open
font (Noto Sans TC) to static Regular/Bold and embeds it via @font-face, instead
of relying on non-redistributable system fonts (PingFang, ...). On macOS install
it with: brew install --cask font-noto-sans-tc

用法 / Usage:
    pip install -e ".[booklet]"
    python scripts/make_booklet.py --size a5
    python scripts/make_booklet.py --size a6 --font 7 --target 7776

封面與聯絡資訊請改下方的 CONFIG 區塊。/ Edit the CONFIG block below for cover text.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FONT_CACHE = REPO / "data" / "interim" / "fonts"  # gitignored build scratch

# ── EDIT ME：社群文案（封面／聯絡／版權頁）/ community front-matter ──────────────
# 換成你們社群的實際介紹與聯絡方式。/ Replace with your community's real copy.
CONFIG = {
    "name": "anoni.net",
    "title": "亞洲風格的 Diceware 密語詞表",
    "subtitle": "An Asian-flavored Diceware wordlist",
    # 封面展示的特色亞洲外來語範例（皆為實際 pin 入的字）。/ Featured loanword
    # samples shown on the cover (all are real pinned entries).
    "features": [
        "tofu",
        "ramen",
        "matcha",
        "kimchi",
        "bibimbap",
        "typhoon",
        "oolong",
        "boba",
        "wonton",
        "ketchup",
        "curry",
        "mango",
        "yoga",
        "karaoke",
        "tsunami",
        "emoji",
        "ninja",
        "zen",
    ],
    "intro_zh": [
        "一份 Diceware 風格的密語詞表，混合好拼好記的常用英文字，以及有字典背書的"
        "亞洲外來語。擲骰子或用亂數抽幾個字，就是一組好記又夠強的密語，全程不用電腦。",
    ],
    "intro_en": [
        "A Diceware-style wordlist that blends easy-to-spell common English words "
        "with dictionary-attested Asian loanwords. Pick a few words with dice or an "
        "RNG and you have a strong, memorable passphrase — no computer required.",
    ],
    # 社群介紹，放在最後的版權頁。/ community blurb, shown on the colophon.
    "about_zh": "anoni.net 是一群關注匿名網路與網路自由的社群，長期透過 Tor、Tails、OONI 等"
    "工具實驗、推廣與分享。我們正在招募夥伴，歡迎加入。",
    "about_en": "anoni.net is a community for anonymous networks and internet freedom — we "
    "experiment with and share tools like Tor, Tails, and OONI, and we are recruiting. "
    "Come join us.",
    "contact": [
        ("Web", "https://anoni.net"),
        ("Docs", "https://anoni.net/docs/"),
        ("Matrix", "https://matrix.to/#/#community:im.anoni.net"),
        ("Email", "whisper@anoni.net（歡迎 PGP / PGP welcome）"),
        ("Repo", "https://github.com/anoni-net/asian-diceware"),
    ],
    "qr_url": "https://anoni.net",
    "qr_caption": "anoni.net",
}
# ──────────────────────────────────────────────────────────────────────────────

PAGE = {
    "a5": {"size": "A5", "cols": 4, "margin": "12mm 8mm 14mm 8mm"},
    "a6": {"size": "A6", "cols": 3, "margin": "8mm 6mm 10mm 6mm"},
}

CSS_TEMPLATE = """
__FONTFACE__
@page { size: __SIZE__; margin: __MARGIN__; }
@page { @bottom-center { content: counter(page); font-family: __FOOTFONT__;
        font-size: 8pt; color: #999; } }
@page :first { @bottom-center { content: none; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: __BODYFONT__; color: #111; }
h1 { font-size: 24pt; }
h2 { font-size: 13pt; margin-bottom: 3mm; border-bottom: 0.4pt solid #ccc;
     padding-bottom: 1mm; }
p { font-size: 9.5pt; line-height: 1.55; margin-bottom: 2.5mm; }
.cover { text-align: center; padding-top: 22mm; break-after: page; }
.cover h1 { font-size: 21pt; line-height: 1.3; }
.cover .subtitle { font-size: 12pt; color: #555; margin-top: 3mm; }
.cover .byline { font-size: 10pt; color: #888; margin-top: 4mm; }
.cover .features { margin-top: 9mm; }
.cover .ftitle { font-size: 10pt; font-weight: 700; color: #444; margin-bottom: 2.5mm; }
.cover .fwords { display: grid; grid-template-columns: repeat(3, 1fr);
                 gap: 1.8mm 4mm; max-width: 88mm; margin: 0 auto;
                 font-family: __MONOFONT__; font-size: 10.5pt; color: #222; }
.cover .fwords span { text-align: center; white-space: nowrap; }
.cover .fnote { font-size: 8pt; color: #777; margin-top: 2.5mm; }
.cover .qr { width: 34mm; height: 34mm; margin: 12mm auto 0; }
.qrcap { font-size: 8pt; color: #777; margin-top: 1mm; text-align: center; }
.qr svg { width: 100%; height: 100%; display: block; }
.howto { break-after: page; }
.howto ol { margin: 0 0 3mm 5mm; font-size: 9.5pt; line-height: 1.6; }
.howto ul { margin: 0 0 3mm 5mm; font-size: 9.5pt; line-height: 1.6; }
.howto .lang.en { break-before: page; }
.example { font-family: __MONOFONT__; font-size: 9pt; background: #f4f4f4;
           padding: 1.5mm 2mm; margin: 1mm 0 2mm; }
.warn { font-size: 9pt; color: #a00; }
.note { font-size: 8.5pt; color: #777; }
.tablehead { break-after: avoid; margin-top: 0; }
.grid { column-count: __COLS__; column-gap: 4mm; column-rule: 0.3pt solid #ddd;
        font-family: __MONOFONT__; font-size: __FONT__pt; line-height: 1.2;
        margin-top: 2mm; }
.e { white-space: nowrap; break-inside: avoid; }
.e .c { color: #888; }
.colophon { break-before: page; }
.colophon ul { list-style: none; margin: 2mm 0; }
.colophon li { font-size: 9pt; margin-bottom: 1mm; }
.colophon .qr { width: 24mm; height: 24mm; margin: 3mm 0 0; }
.colophon .qrcap { text-align: left; width: 24mm; }
.cover .ver { font-size: 8pt; color: #aaa; margin-top: 8mm; }
.colophon .version { font-family: __MONOFONT__; font-size: 8.5pt; color: #555;
                     margin: 4mm 0; }
.blank { break-before: page; }
"""


def load_entries(target: int) -> list[tuple[str, str]]:
    """讀 dice 檔，回傳 (擲骰碼, 字) 串列。/ Read the dice file into (roll, word)."""
    path = REPO / "output" / f"asian_diceware_{target}_dice.txt"
    if not path.exists():
        sys.exit(f"missing {path}\n  run the pipeline first: ./scripts/run_pipeline.sh {target}")
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        roll, word = line.split("\t")
        rows.append((roll, word))
    return rows


def wordlist_version() -> str:
    """從 pyproject 讀版本號。/ Read the version from pyproject."""
    try:
        with (REPO / "pyproject.toml").open("rb") as f:
            return "v" + tomllib.load(f)["project"]["version"]
    except Exception:
        return "dev"


def wordlist_fingerprint(entries: list[tuple[str, str]], length: int = 12) -> str:
    """詞表內容的 SHA-256 短指紋（字詞一變就變）。/ Short SHA-256 of the word set
    (changes whenever the words change), matching output/asian_diceware_<n>.txt."""
    body = "\n".join(w for _, w in entries) + "\n"
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:length]


def _fc_query(name: str) -> Path | None:
    """用 fc-match 找字型檔，且回傳的家族名需真的對得上。
    Locate a font file via fc-match, only if the matched family really matches."""
    if not shutil.which("fc-match"):
        return None
    try:
        out = subprocess.run(
            ["fc-match", "-f", "%{family}|%{file}", name],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except Exception:
        return None
    fam, _, file = out.partition("|")
    file = file.strip()
    if name.lower() in fam.lower() and file:
        return Path(file)
    return None


def find_font(names: list[str]) -> Path | None:
    """依序找開源字型，找不到回傳 None。/ Find an open font by name list, or None."""
    for n in names:
        p = _fc_query(n)
        if p and p.exists():
            return p
    cand = Path.home() / "Library" / "Fonts" / "NotoSansTC[wght].ttf"  # macOS fallback
    if "Noto Sans TC" in names and cand.exists():
        return cand
    return None


def as_static(src: Path, weight: int) -> Path:
    """變數字型實例成指定 weight 的靜態 TTF（weasyprint 對變數字型的逐字 fallback 會誤用
    系統字型，靜態化可避免）。靜態字型直接回傳原檔。
    Instance a variable font to a static TTF at the given weight (weasyprint's
    per-glyph fallback misbehaves with variable fonts). Static fonts are returned
    as-is."""
    from fontTools import ttLib

    font = ttLib.TTFont(src)
    if "fvar" not in font:
        return src
    from fontTools.varLib.instancer import instantiateVariableFont

    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    stem = src.stem.replace("[", "_").replace("]", "_")
    dst = FONT_CACHE / f"{stem}-{weight}.ttf"
    if not dst.exists():
        instantiateVariableFont(font, {"wght": weight}, inplace=True)
        font.save(dst)
    return dst


def build_faces() -> dict:
    """找並準備可嵌入的開源字型。/ Locate and prepare embeddable open fonts."""
    faces: dict = {}
    cjk = find_font(["Noto Sans TC", "Noto Sans CJK TC", "Source Han Sans TC"])
    if cjk:
        faces["cjk_reg"] = as_static(cjk, 400)
        faces["cjk_bold"] = as_static(cjk, 700)
    mono = find_font(["JetBrains Mono", "DejaVu Sans Mono", "Noto Sans Mono"])
    if mono:
        faces["mono"] = as_static(mono, 400)
    return faces


def qr_svg(url: str, scale: int = 4) -> str:
    """以 segno 產生內嵌 SVG 的 QR。/ Inline-SVG QR via segno."""
    import segno

    return segno.make(url, error="m").svg_inline(scale=scale, border=2)


def _entries_html(entries: list[tuple[str, str]]) -> str:
    cells = [
        f'<div class="e"><span class="c">{roll}</span>&#160;{html.escape(word)}</div>'
        for roll, word in entries
    ]
    return "".join(cells)


def _fontface_css(faces: dict) -> tuple[str, str, str, str]:
    """回傳 (@font-face 區塊, body 字型, mono 字型, footer 字型)。
    Return (@font-face rules, body font, mono font, footer font). When embeddable
    open fonts are found we drop the generic families entirely so weasyprint never
    pulls a non-redistributable system font (Noto Sans TC covers every glyph used).
    """
    rules: list[str] = []
    has_cjk = bool(faces.get("cjk_reg"))
    has_mono = bool(faces.get("mono"))
    body = "'Noto Sans TC','Noto Sans CJK TC','PingFang TC',sans-serif"
    mono = "'JetBrains Mono','DejaVu Sans Mono','Menlo',monospace"
    foot = "sans-serif"
    if has_cjk:
        rules.append(
            "@font-face{font-family:'Booklet CJK';font-weight:400;"
            f"src:url('{faces['cjk_reg'].resolve().as_uri()}');}}"
        )
        if faces.get("cjk_bold"):
            rules.append(
                "@font-face{font-family:'Booklet CJK';font-weight:700;"
                f"src:url('{faces['cjk_bold'].resolve().as_uri()}');}}"
            )
        body = "'Booklet CJK'"
        foot = "'Booklet CJK'"
    if has_mono:
        rules.append(
            "@font-face{font-family:'Booklet Mono';font-weight:400;"
            f"src:url('{faces['mono'].resolve().as_uri()}');}}"
        )
        mono = "'Booklet Mono','Booklet CJK'" if has_cjk else "'Booklet Mono',monospace"
    elif has_cjk:
        mono = "'JetBrains Mono','DejaVu Sans Mono','Booklet CJK',monospace"
    return "\n".join(rules), body, mono, foot


def render_html(
    size_key: str,
    font_pt: float,
    entries: list[tuple[str, str]],
    cfg: dict,
    faces: dict | None = None,
    blanks: int = 0,
) -> str:
    """組出整本小冊的 HTML 字串。/ Build the full booklet HTML string."""
    pg = PAGE[size_key]
    fontface, bodyfont, monofont, footfont = _fontface_css(faces or {})
    css = (
        CSS_TEMPLATE.replace("__FONTFACE__", fontface)
        .replace("__BODYFONT__", bodyfont)
        .replace("__MONOFONT__", monofont)
        .replace("__FOOTFONT__", footfont)
        .replace("__SIZE__", pg["size"])
        .replace("__MARGIN__", pg["margin"])
        .replace("__COLS__", str(pg["cols"]))
        .replace("__FONT__", f"{font_pt}")
    )
    name = html.escape(cfg["name"])
    title = html.escape(cfg["title"])
    subtitle = html.escape(cfg["subtitle"])
    cap = html.escape(cfg["qr_caption"])
    qr = qr_svg(cfg["qr_url"])
    intro_zh = "".join(f"<p>{html.escape(p)}</p>" for p in cfg["intro_zh"])
    intro_en = "".join(f"<p>{html.escape(p)}</p>" for p in cfg["intro_en"])
    contacts = "".join(
        f"<li><b>{html.escape(k)}</b>&#160;&#160;{html.escape(v)}</li>" for k, v in cfg["contact"]
    )
    about_zh = html.escape(cfg["about_zh"])
    about_en = html.escape(cfg["about_en"])
    feat_words = "".join(f"<span>{html.escape(w)}</span>" for w in cfg.get("features", []))
    features = (
        (
            '<div class="features">'
            '<div class="ftitle">特色亞洲字詞 / Featured Asian loanwords</div>'
            f'<div class="fwords">{feat_words}</div>'
            '<div class="fnote">字典查證入選的亞洲外來語 / dictionary-attested, hand-picked</div>'
            "</div>"
        )
        if feat_words
        else ""
    )
    grid = _entries_html(entries)
    blanks_html = '<div class="blank">&#160;</div>' * blanks
    count = f"{len(entries):,}"
    version = wordlist_version()
    fp = wordlist_fingerprint(entries)

    body = f"""
<section class="cover">
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  <div class="byline">{name}</div>
  {features}
  <div class="qr">{qr}</div>
  <div class="qrcap">{cap}</div>
  <div class="ver">{version}</div>
</section>
<section class="howto">
  <div class="lang">
    <h2>關於這份字典表</h2>
    {intro_zh}
    <h2>什麼時候用</h2>
    <ul>
      <li>密碼管理員、email 等重要帳號的主密碼。</li>
      <li>全磁碟加密與開機密碼。</li>
      <li>PGP 金鑰、加密備份、Tails 持續磁區的通行碼。</li>
      <li>需要唸出來或手抄傳遞的密碼，好唸好拼、不易抄錯。</li>
      <li>在不信任的電腦旁，用實體骰子離線產生，全程不經過任何裝置。</li>
    </ul>
    <h2>怎麼用</h2>
    <ol>
      <li>擲 5 顆骰子，由左到右讀成五位數（每顆 1–6）。</li>
      <li>在查表找那個數字，抄下對應的字。</li>
      <li>重複 6 次，用「-」把字連起來。</li>
      <li>六個字的組合多到天文數字，就算電腦每秒猜十億次，平均也要上百萬年才猜得中，足以保護重要帳號（約 77.5 bits 的強度）。</li>
    </ol>
    <div class="example">例：6 3 4 4 4 → 63444 → tofu</div>
    <p class="warn">務必用真的骰子或密碼學亂數，不要自己挑字。</p>
    <h2>還可以怎麼用</h2>
    <ul>
      <li>兩人暗號：見面時一起擲一組字、各自記住。日後互報這組字，確認對方是本人。暗號要保密，最好一次性使用。</li>
      <li>把號碼唸成字：要核對一串數字（像金鑰指紋）時，用這張表把號碼換成字來唸，比唸一長串數字不容易聽錯。</li>
    </ul>
    <p class="note">這張表本身是公開的、不提供加密，只是讓共用的數值好唸好核對。安全與否取決於你怎麼交換與保管那個數值。兩人也要確認用的是同一版（核對封底的版本與 SHA-256）。</p>
  </div>
  <div class="lang en">
    <h2>About this wordlist</h2>
    {intro_en}
    <h2>When to use it</h2>
    <ul>
      <li>A master password for a password manager, email, or other key account.</li>
      <li>Full-disk encryption and login or boot passwords.</li>
      <li>Passphrases for PGP keys, encrypted backups, or a Tails persistent volume.</li>
      <li>Passwords you read aloud or copy by hand — easy to say, spell, and type.</li>
      <li>Generating offline with real dice beside an untrusted computer (air-gapped).</li>
    </ul>
    <h2>How to use</h2>
    <ol>
      <li>Roll 5 dice, read left to right as a five-digit number (each die 1–6).</li>
      <li>Find that number in the table and copy the word next to it.</li>
      <li>Repeat six times and join the words with “-”.</li>
      <li>Six words make so many combinations that a computer guessing a billion times a second would need millions of years on average — plenty for important accounts (about 77.5 bits).</li>
    </ol>
    <div class="example">e.g.&#160;&#160;6 3 4 4 4 → 63444 → tofu</div>
    <p class="warn">Always use real dice or a CSPRNG; never hand-pick.</p>
    <h2>Other uses</h2>
    <ul>
      <li>A recognition phrase for two people: roll one together in person, each keep it, and later exchange it to confirm you are really each other. Keep it secret; use it once.</li>
      <li>Reading a number aloud: turn a value like a key fingerprint into words with this table — easier to dictate than raw digits.</li>
    </ul>
    <p class="note">The list adds no encryption by itself; it only makes a shared value easy to compare. Security depends on how you exchange it, and both sides must use the same version (see the back-page SHA-256).</p>
  </div>
</section>
<h2 class="tablehead">擲骰查表 / Roll → word（{count} 字 / words）</h2>
<div class="grid">{grid}</div>
<section class="colophon">
  <h2>關於 anoni.net / About anoni.net</h2>
  <p>{about_zh}</p>
  <p>{about_en}</p>
  <ul>{contacts}</ul>
  <h2>授權與出處 / License &amp; credits</h2>
  <p>詞表資料 © anoni.net，採 CC-BY-4.0。程式碼 MIT。
     Wordlist data © anoni.net, licensed CC-BY-4.0; code MIT.</p>
  <p>Diceware 風格，建立在 EFF 與 A. G. Reinhold 的前作之上。
     Diceware-style, building on prior art by the EFF and A. G. Reinhold.</p>
  <div class="version">版本 / Version {version} · {count} words · SHA-256 {fp}</div>
  <div class="qr">{qr}</div>
  <div class="qrcap">{cap}</div>
</section>
{blanks_html}
"""
    return (
        "<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'>"
        f"<style>{css}</style></head><body>{body}</body></html>"
    )


def build(
    size_key: str,
    font_pt: float,
    entries: list[tuple[str, str]],
    cfg: dict,
    faces: dict,
    pad: bool = True,
):
    """渲染，必要時補白頁讓總頁數為 4 的倍數（騎馬釘）。
    Render; pad with blank pages to a multiple of 4 (saddle-stitch) when asked."""
    from weasyprint import HTML

    doc = HTML(string=render_html(size_key, font_pt, entries, cfg, faces)).render()
    n = len(doc.pages)
    if pad and n % 4:
        blanks = 4 - (n % 4)
        doc = HTML(
            string=render_html(size_key, font_pt, entries, cfg, faces, blanks=blanks)
        ).render()
    return doc, len(doc.pages)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Make a printable Diceware lookup booklet (PDF).")
    ap.add_argument("--target", type=int, default=7776)
    ap.add_argument("--size", choices=["a5", "a6"], default="a5")
    ap.add_argument("--font", type=float, default=7.0, help="table font size in pt")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-pad", action="store_true", help="do not pad to a multiple of 4 pages")
    args = ap.parse_args(argv)

    try:
        import segno  # noqa: F401
        from weasyprint import HTML  # noqa: F401
    except ImportError as exc:
        sys.exit(f'missing dependency ({exc.name}); install with: pip install -e ".[booklet]"')

    entries = load_entries(args.target)
    if len(entries) != args.target:
        sys.exit(f"{len(entries)} entries != target {args.target}; rebuild the list first")

    faces = build_faces()
    if not faces.get("cjk_reg"):
        print(
            "warning: no embeddable open CJK font found (Noto Sans TC / Source Han Sans).\n"
            "  Chinese may not display for other viewers. Install it and re-run:\n"
            "  macOS: brew install --cask font-noto-sans-tc",
            file=sys.stderr,
        )

    out = args.out or (REPO / "output" / f"asian_diceware_{args.target}_booklet_{args.size}.pdf")
    doc, pages = build(args.size, args.font, entries, CONFIG, faces, pad=not args.no_pad)
    doc.write_pdf(out)
    cjk = "Booklet CJK (embedded)" if faces.get("cjk_reg") else "system fallback"
    print(
        f"wrote {out}\n  {pages} pages · {args.size.upper()} · {args.font}pt · "
        f"{len(entries):,} entries · CJK: {cjk}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
