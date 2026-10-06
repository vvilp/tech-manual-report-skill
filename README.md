# tech-manual-report

A [Claude Code](https://claude.com/claude-code) skill that writes HTML and PDF reports in a "technical manual" style. One HTML source gives you both:

- a web page you scroll through, and
- a US Letter PDF with running headers, page numbers, a contents page with real page numbers, and `(p. 33)` cross-references.

![Example pages](docs/preview.png)

## The look

- **Paper and ink.** Warm off-white pages with navy text, hairline rules, and no shadows or gradients.
- **Type.** Headings in Manrope and body text in Source Sans 3. Each section opens with a short summary in Source Serif 4 italic. Labels, code and citations use JetBrains Mono, with labels in spaced-out capitals.
- **Pages.** A cover with a diagram and a numbered key. A contents page with dotted leaders. Dark full-page part dividers with a large faded part number. Numbered sections.
- **Parts.** `FIG. 1.2` diagram panels with captions. Warning, rule, tip and note callouts. "What this means for you" summary boxes. Code blocks, tables and KPI tiles, plus a `Sources:` line at the end of a section.
- **Diagrams.** Box diagrams are built with HTML classes. Sequence diagrams and timelines use a set of shared SVG classes.

See `examples/example.pdf` and `examples/example.html` for the full sample.

## Install

Clone into your personal skills folder (all projects):

```bash
git clone https://github.com/<you>/tech-manual-report ~/.claude/skills/tech-manual-report
```

Or clone into one project's `.claude/skills/` folder instead.

Then ask Claude Code for a report "in the technical manual style", or run `/tech-manual-report`.

### Requirements

- Python 3.9+ (standard library only)
- To make PDFs, one of:
  - [WeasyPrint](https://weasyprint.org) (recommended): `brew install weasyprint` or `pip install weasyprint`
  - Google Chrome / Chromium, with `--engine chrome`. This engine leaves running section titles, contents page numbers and cross-reference page numbers blank.
- `pdftoppm` (poppler), if you want to preview PDF pages as images

## Use without Claude

```bash
cp assets/template.html my-report.html     # edit the content
python3 scripts/build.py my-report.html --html out.html --pdf out.pdf
```

| Option | Effect |
|---|---|
| `--fonts google` | Default for HTML. Small file; loads fonts from Google Fonts. |
| `--fonts embed` | Puts the fonts inside the HTML file. Works offline; about 2.7 MB. |
| `--engine weasyprint` / `--engine chrome` | Chooses the PDF renderer. |

Two `<meta>` tags in the source set the running header and footer:
`<meta name="doc-short" content="…">` and `<meta name="doc-footer" content="…">`.

## Layout

```
SKILL.md                 instructions Claude follows
assets/theme.css         the theme (screen + print)
assets/template.html     a sample report using every component
assets/fonts/            bundled TTFs + their OFL licenses
references/components.md markup for each component, palette, diagram rules
scripts/build.py         HTML/PDF builder
examples/                the template, built
```

## Credits

The visual style is modeled on the *Pi Durable Technical Manual*. The fonts are distributed under the SIL Open Font License 1.1. Copyright notices and the license text are in `assets/fonts/OFL-*.txt`.
