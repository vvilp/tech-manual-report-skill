#!/usr/bin/env python3
"""Build a themed report from a content HTML file.

    python3 build.py report.html --html out.html --pdf out.pdf [--theme minimal]
    python3 build.py --list-themes

The input is a normal HTML document whose <body class="manual"> uses the theme's
components (see assets/template.html). This script:

  1. injects the chosen theme's stylesheet and fonts into <head>;
  2. fills the running header / footer strings from two <meta> tags:
       <meta name="doc-short"  content="Short title">                  (top-right of every page)
       <meta name="doc-footer" content="Short title / Document type">  (bottom-left of every page)
  3. writes a standalone HTML file and/or renders a PDF.

Themes live in assets/themes/<name>/ (theme.css + theme.json). Choose one with
--theme <name>, or put <meta name="report-theme" content="<name>"> in the source.
The command-line flag wins; the default is "manual".

Fonts:  --fonts google  link Google Fonts (small file, needs internet to view)
        --fonts embed   base64-embed the bundled TTFs (fully offline, ~2.6 MB)
        --fonts local   reference the bundled TTFs by absolute file:// path (used for PDF)

PDF engines:
  weasyprint (default)  full paged-media support: running section titles, TOC page
                        numbers, "(p. 33)" cross-references.
  chrome                headless Google Chrome; page numbers and margin boxes work,
                        but string-set (running section title) and target-counter
                        (TOC / xref page numbers) are not supported, so those are blank.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
FONTS = ASSETS / "fonts"

THEMES = ASSETS / "themes"
DEFAULT_THEME = "manual"


def available_themes() -> list[str]:
    return sorted(p.name for p in THEMES.iterdir() if (p / "theme.css").exists() and (p / "theme.json").exists())


def load_theme(name: str) -> dict:
    d = THEMES / name
    if not (d / "theme.css").exists():
        sys.exit(f"unknown theme {name!r}; available: {', '.join(available_themes())}")
    cfg = json.loads((d / "theme.json").read_text())
    cfg["css"] = (d / "theme.css").read_text()
    return cfg


def google_link(cfg: dict) -> str:
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{cfg["google_fonts"]}&display=swap">'
    )


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]


def font_css(cfg: dict, mode: str) -> str:
    if mode == "google":
        return ""
    rules = []
    for family, stem, weight, style in cfg["fonts"]:
        path = FONTS / f"{stem}.ttf"
        if mode == "embed":
            src = "data:font/ttf;base64," + base64.b64encode(path.read_bytes()).decode()
        else:
            src = path.as_uri()
        rules.append(
            f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:{style};'
            f'font-display:swap;src:url("{src}") format("truetype");}}'
        )
    return "\n".join(rules)


def css_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def meta(doc: str, name: str) -> str | None:
    m = re.search(
        rf'<meta\s+[^>]*name=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)["\']', doc, re.I
    ) or re.search(
        rf'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']{re.escape(name)}["\']', doc, re.I
    )
    return html.unescape(m.group(1)) if m else None


def assemble(src: str, fonts: str, cfg: dict) -> str:
    title = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
    short = meta(src, "doc-short") or (html.unescape(title.group(1)).strip() if title else "")
    footer = meta(src, "doc-footer") or (short + " / Report" if short else "")
    page_css = (
        "@page{"
        f"@top-right{{content:{css_string(short)};{cfg['running_head']}}}"
        f"@bottom-left{{content:{css_string(footer.upper() if cfg.get('foot_uppercase') else footer)};{cfg['running_foot']}}}"
        "}"
        "@page front{@top-right{content:none}@bottom-left{content:none}}"
        "@page cover{@top-right{content:none}@bottom-left{content:none}}"
        "@page part{@top-right{content:none}@bottom-left{content:none}}"
        f".part-foot .doc::before{{content:{css_string(footer)};}}"
    )
    theme = cfg["css"]
    head_inject = (
        (google_link(cfg) if fonts == "google" else "")
        + "<style>\n" + font_css(cfg, fonts) + "\n" + theme + "\n" + page_css + "\n</style>"
    )
    # drop a theme.css link the author may have used for local preview
    src = re.sub(r'<link[^>]+href=["\'][^"\']*theme\.css["\'][^>]*>\s*', "", src, flags=re.I)
    src = inline_svg_kit(src, theme)
    if "<!-- THEME -->" in src:
        return src.replace("<!-- THEME -->", head_inject, 1)
    if re.search(r"</head>", src, re.I):
        return re.sub(r"</head>", head_inject + "\n</head>", src, count=1, flags=re.I)
    return f"<!doctype html><html><head><meta charset='utf-8'>{head_inject}</head><body class='manual'>{src}</body></html>"


def inline_svg_kit(doc: str, theme: str) -> str:
    """Copy the SVG kit rules into every <svg class="diagram">: PDF engines do not
    apply the page stylesheet to inline SVG, but they honour a <style> inside it."""
    a = theme.find("/* ---------- inline SVG diagram kit")
    b = theme.find("/* ---------- misc")
    if a < 0 or b < 0:
        return doc
    kit = re.sub(r"/\*.*?\*/", "", theme[a:b], flags=re.S)
    kit = kit.replace("svg.diagram {", ":root {").replace("svg.diagram ", "")
    style = "<style>" + kit + "</style>"
    return re.sub(r'(<svg\b[^>]*class=["\'][^"\']*\bdiagram\b[^"\']*["\'][^>]*>)',
                  lambda m: m.group(1) + style, doc)


EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\u2B1B\u2B1C\u231A\u231B\u23E9-\u23FA\u24C2"
    "\u2934\u2935\u3030\u303D\u3297\u3299\u00A9\u00AE\u203C\u2049\u2122\u2139]"
    "[\uFE0E\uFE0F\u200D\u20E3\U0001F3FB-\U0001F3FF]*[ ]?"
    "|[\uFE0F\u20E3]"
)


def strip_emoji(src: str) -> tuple[str, list[str]]:
    """Reports contain no emoji. Remove pictographs (and the space after each) and
    return the distinct characters removed so the caller can warn."""
    found = sorted({m.group(0).strip() for m in EMOJI_RE.finditer(src)} - {""})
    return EMOJI_RE.sub("", src), found


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def render_pdf(doc: str, out: Path, engine: str, base: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        # keep the temp file next to the source so relative image paths resolve
        tmp = base / f".__tmr_build_{Path(td).name}.html"
        tmp.write_text(doc)
        try:
            if engine == "weasyprint":
                exe = shutil.which("weasyprint")
                if not exe:
                    sys.exit("weasyprint not found (brew install weasyprint / pip install weasyprint); try --engine chrome")
                r = subprocess.run([exe, "--quiet", str(tmp), str(out)], capture_output=True, text=True)
                if r.returncode != 0:
                    sys.exit("weasyprint failed:\n" + r.stderr)
            else:
                exe = find_chrome()
                if not exe:
                    sys.exit("Chrome/Chromium not found; try --engine weasyprint")
                r = subprocess.run(
                    [exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                     "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
                     f"--print-to-pdf={out}", tmp.as_uri()],
                    capture_output=True, text=True, timeout=180,
                )
                if not out.exists():
                    sys.exit("chrome failed:\n" + r.stderr)
        finally:
            tmp.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, nargs="?", help="content HTML file")
    ap.add_argument("--html", type=Path, help="write standalone themed HTML here")
    ap.add_argument("--pdf", type=Path, help="write PDF here")
    ap.add_argument("--theme", help=f"theme name (default: <meta name=report-theme> or {DEFAULT_THEME!r})")
    ap.add_argument("--list-themes", action="store_true", help="list available themes and exit")
    ap.add_argument("--fonts", choices=["google", "embed", "local"], default=None,
                    help="font delivery for --html (default: google). PDF always uses local fonts.")
    ap.add_argument("--keep-emoji", action="store_true",
                    help="do not strip emoji / pictograph characters (stripped by default)")
    ap.add_argument("--engine", choices=["weasyprint", "chrome"], default="weasyprint")
    a = ap.parse_args()
    if a.list_themes:
        for name in available_themes():
            print(f"{name:10} {json.loads((THEMES / name / 'theme.json').read_text()).get('description', '')}")
        return
    if not a.input:
        ap.error("give an input HTML file")
    if not a.html and not a.pdf:
        ap.error("give --html and/or --pdf")

    src = a.input.read_text()
    if not a.keep_emoji:
        src, removed = strip_emoji(src)
        if removed:
            print(f"warning: removed emoji from output: {' '.join(removed)}  (fix the source; --keep-emoji to allow)", file=sys.stderr)
    theme_name = a.theme or meta(src, "report-theme") or DEFAULT_THEME
    cfg = load_theme(theme_name)
    if a.html:
        a.html.write_text(assemble(src, a.fonts or "google", cfg))
        print(f"html: {a.html}  (theme: {theme_name})")
    if a.pdf:
        render_pdf(assemble(src, "local", cfg), a.pdf.resolve(), a.engine, a.input.resolve().parent)
        print(f"pdf:  {a.pdf}  (theme: {theme_name})")


if __name__ == "__main__":
    main()
