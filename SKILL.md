---
name: tech-manual-report
description: >-
  Apply the "Technical Manual" visual theme to an HTML and/or PDF report — warm paper background, navy ink, Manrope headings, Source Serif italic summary lines, JetBrains Mono letterspaced labels, dark part-divider pages with giant numerals, numbered sections, FIG.-labelled panels, callouts, tables and code blocks. Theme only: it changes how a document looks, never what it says. Use when the user wants a report, manual, handbook or write-up produced as a styled HTML or PDF in this theme (e.g. "in the technical manual style", "like the Pi Durable PDF"), whether they supply the content or ask for it to be written separately.
---

# Technical Manual report theme

This skill is a **visual theme and a builder**. It turns content into a themed web page and a paginated US‑Letter PDF (running headers, page numbers, contents page with real page numbers, `(p. N)` cross-references). It has **no opinion about content or wording.**

## Scope: theme only

- **Do not change the user's words.** Keep their headings, sentences, terminology, tone, structure and order. Do not rewrite, shorten, "improve" or reformat prose into a house voice.
- **Do not add content the user did not ask for**: no summary lines, "what this means" boxes, sources lines, citations, callouts, KPI tiles, figures, glossaries or key-takeaway sections. Use a component only when the user's content already contains that kind of thing (a table → table, a code sample → code block, a warning they wrote → callout).
- **Do not invent diagrams or data** to fill a cover or a page. If there is nothing to draw, leave the optional cover plate out.
- Titles, labels, part names and numbering come from the user's content. If something needed by the theme is missing (a title, a date), ask or leave it out; do not write one.
- If the user also wants the content *written* (research, drafting), that is a separate step with its own style requirements. Do that first, then apply this theme to the result.
- Nothing in `assets/template.html` or `references/components.md` is wording to reuse; it is placeholder text showing markup only.

## Files

| Path | What it is |
|---|---|
| `assets/theme.css` | The theme (screen + `@media print` + `@page`). Do not edit per report; add a small `<style>` in the report if a one-off tweak is needed. |
| `assets/template.html` | Every component with placeholder text. Copy the parts you need. |
| `assets/fonts/` | Bundled static TTFs (Manrope, Source Sans 3, Source Serif 4 italic, JetBrains Mono) with their OFL licenses. |
| `scripts/build.py` | Injects theme + fonts and writes standalone HTML and/or renders PDF. |
| `references/components.md` | Markup, class names and palette for each component. |
| `examples/example.pdf`, `examples/example.html` | The template built, to show the look. |

## Workflow

1. **Get the content** (the user's file, text, or an existing document). Work out its structure as it is: parts → sections → subsections. Don't restructure it.
2. **Start from `assets/template.html`.** Keep `<!-- THEME -->`, set `<title>`, `<meta name="doc-short">` (top-right running head) and `<meta name="doc-footer">` (bottom-left footer) from the user's document title. Delete placeholder components that the content does not use.
3. **Pour the content into the components** in `references/components.md`, preserving the text exactly (escape `<`, `>`, `&`). Give each part its colour class `c-blue, c-teal, c-violet, c-green, c-amber, c-rose, c-indigo, c-plum, c-forest, c-slate` in order, on the part divider, its sections and its contents entry.
   - Short document (1–4 pages): skip the contents page and part dividers; use a title block plus `.chapter` sections.
4. **Build:**
   ```bash
   python3 <skill>/scripts/build.py report.html --html out.html --pdf out.pdf
   ```
   - `--fonts google` (default for HTML) or `--fonts embed` for a fully offline single file (~2.7 MB).
   - PDF engine: `weasyprint` (default, full support) or `--engine chrome` (no running section title, no contents/cross-reference page numbers). Install with `brew install weasyprint` or `pip install weasyprint`.
   - Never overwrite the source file with built output.
5. **Verify visually.** Render pages to PNG and look at them (`pdftoppm -r 60 -png out.pdf <dir>/p`):
   cover fits on one page; part dividers are full dark pages; contents page numbers are filled; no SVG shapes render black; no overflow in panels; no heading stranded at the bottom of a page. For HTML, check desktop and phone width.
6. Tell the user where the files are.

## Look rules

- Palette and typography are fixed (see `references/components.md`). Don't add colour backgrounds to body text, emoji, shadows or gradients; the style is flat and hairline-ruled.
- In inline SVG, set colours with the kit classes or literal hex in `style="fill:#…"`; never `var(--…)` (PDF engines ignore it). `build.py` copies the SVG kit styles into each `<svg class="diagram">`.
