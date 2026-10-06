#!/usr/bin/env python3
"""Build a Technical Manual themed report from a content HTML file.

    python3 build.py report.html --html out.html --pdf out.pdf

The input is a normal HTML document whose <body class="manual"> uses the theme's
components (see assets/template.html). This script:

  1. injects the theme stylesheet and fonts into <head>;
  2. fills the running header / footer strings from two <meta> tags:
       <meta name="doc-short"  content="Short title">                  (top-right of every page)
       <meta name="doc-footer" content="Short title / Document type">  (bottom-left of every page)
  3. writes a standalone HTML file and/or renders a PDF.

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
import argparse
import base64
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
FONTS = ASSETS / "fonts"

FACES = [
    # family, file stem, weight, style
    ("Manrope", "Manrope-500", 500, "normal"),
    ("Manrope", "Manrope-600", 600, "normal"),
    ("Manrope", "Manrope-700", 700, "normal"),
    ("Manrope", "Manrope-800", 800, "normal"),
    ("Source Sans 3", "SourceSans3-400", 400, "normal"),
    ("Source Sans 3", "SourceSans3-400-italic", 400, "italic"),
    ("Source Sans 3", "SourceSans3-600", 600, "normal"),
    ("Source Sans 3", "SourceSans3-700", 700, "normal"),
    ("Source Serif 4", "SourceSerif4-400-italic", 400, "italic"),
    ("Source Serif 4", "SourceSerif4-500-italic", 500, "italic"),
    ("JetBrains Mono", "JetBrainsMono-400", 400, "normal"),
    ("JetBrains Mono", "JetBrainsMono-500", 500, "normal"),
    ("JetBrains Mono", "JetBrainsMono-700", 700, "normal"),
]

GOOGLE_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Manrope:wght@500;600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400"
    "&family=Source+Serif+4:ital,opsz,wght@1,8..60,400;1,8..60,500"
    '&family=JetBrains+Mono:wght@400;500;700&display=swap">'
)

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]


def font_css(mode: str) -> str:
    if mode == "google":
        return ""
    rules = []
    for family, stem, weight, style in FACES:
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


def assemble(src: str, fonts: str) -> str:
    title = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
    short = meta(src, "doc-short") or (html.unescape(title.group(1)).strip() if title else "")
    footer = meta(src, "doc-footer") or (short + " / Report" if short else "")
    page_css = (
        "@page{"
        f"@top-right{{content:{css_string(short)};font:400 7.5pt 'Source Sans 3',sans-serif;color:#5f6772;vertical-align:bottom;padding-bottom:8pt;}}"
        f"@bottom-left{{content:{css_string(footer.upper())};font:400 6.8pt 'JetBrains Mono',monospace;letter-spacing:.22em;color:#878e97;vertical-align:top;padding-top:15pt;}}"
        "}"
        "@page front{@top-right{content:none}@bottom-left{content:none}}"
        "@page cover{@top-right{content:none}@bottom-left{content:none}}"
        "@page part{@top-right{content:none}@bottom-left{content:none}}"
        f".part-foot .doc::before{{content:{css_string(footer)};}}"
    )
    theme = (ASSETS / "theme.css").read_text()
    head_inject = (
        (GOOGLE_LINK if fonts == "google" else "")
        + "<style>\n" + font_css(fonts) + "\n" + theme + "\n" + page_css + "\n</style>"
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
    ap.add_argument("input", type=Path, help="content HTML file")
    ap.add_argument("--html", type=Path, help="write standalone themed HTML here")
    ap.add_argument("--pdf", type=Path, help="write PDF here")
    ap.add_argument("--fonts", choices=["google", "embed", "local"], default=None,
                    help="font delivery for --html (default: google). PDF always uses local fonts.")
    ap.add_argument("--engine", choices=["weasyprint", "chrome"], default="weasyprint")
    a = ap.parse_args()
    if not a.html and not a.pdf:
        ap.error("give --html and/or --pdf")

    src = a.input.read_text()
    if a.html:
        a.html.write_text(assemble(src, a.fonts or "google"))
        print(f"html: {a.html}")
    if a.pdf:
        render_pdf(assemble(src, "local"), a.pdf.resolve(), a.engine, a.input.resolve().parent)
        print(f"pdf:  {a.pdf}")


if __name__ == "__main__":
    main()
