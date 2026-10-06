---
name: tech-manual-report
description: >-
  Apply a visual theme to an HTML and/or PDF report. Two themes: "manual" (Technical Manual look — warm paper, navy ink, Manrope headings, Source Serif italic summary lines, JetBrains Mono labels, dark part-divider pages with giant numerals) and "minimal" (modern, clean and minimalist — white page, Inter throughout, one accent colour per part, soft rounded panels, generous spacing). Theme only — it changes how a document looks, never what it says. Use when the user wants a report, manual, handbook or write-up produced as a styled HTML or PDF, names either theme, or asks for the "technical manual style" or a clean minimal report.
---

# Report themes

This skill is a set of **visual themes and a builder**. It turns content into a themed web page and a paginated US‑Letter PDF (running headers, page numbers, contents page with real page numbers, `(p. N)` cross-references). It has **no opinion about content or wording.**

## Scope: theme only

- **Do not change the user's words.** Keep their headings, sentences, terminology, tone, structure and order. Do not rewrite, shorten, "improve" or reformat prose into a house voice.
- **Do not add content the user did not ask for**: no summary lines, "what this means" boxes, sources lines, citations, callouts, KPI tiles, figures, glossaries or key-takeaway sections. Use a component only when the user's content already contains that kind of thing (a table → table, a code sample → code block, a warning they wrote → callout).
- **Do not invent diagrams or data** to fill a cover or a page.
- Titles, labels, part names and numbering come from the user's content. If something needed by the theme is missing (a title, a date), ask or leave it out; do not write one.
- If the user also wants the content *written* (research, drafting), that is a separate step with its own style requirements. Do that first, then apply this theme to the result.
- Nothing in `assets/template.html` or `references/components.md` is wording to reuse; it is placeholder text showing markup only.

## No emoji

Reports never contain emoji or pictograph symbols (checkmarks, warning signs, stars, rockets, flags, coloured circles, keycaps), including in headings, callout labels, table cells, list bullets and diagram text. If the source has them, drop them and keep the words. Use plain text labels ("Warning", "Yes", "No") only if the user's own text already says so; do not substitute new wording. `build.py` strips emoji from the output and prints a warning (`--keep-emoji` disables this). Plain typographic characters such as arrows, middots and dashes are fine.

## Themes

| Theme | Look | Best for |
|---|---|---|
| `manual` (default) | Warm paper, navy ink, Manrope / Source Sans 3 / Source Serif italic / JetBrains Mono, dark part-divider pages, letterspaced mono labels | Technical manuals, engineering references, dense documents |
| `minimal` | White page, Inter throughout, one accent colour per part, tinted part pages, rounded soft panels, generous spacing | Reports, briefings, proposals, anything meant to be pleasant to read |

**Choosing a theme:** use the theme the user names. If they haven't named one, ask once which they want (show the two rows above); if they have no preference, use `manual`. Run `python3 <skill>/scripts/build.py --list-themes` to see installed themes.

Both themes use the **same HTML and class names**, so a report can be rebuilt in the other theme without editing it. Set the theme with `--theme <name>` on the build command, or with `<meta name="report-theme" content="minimal">` in the report's `<head>` (the flag wins).

## Files

| Path | What it is |
|---|---|
| `assets/themes/<name>/theme.css` | A theme's stylesheet (screen + `@media print` + `@page`). Do not edit per report; add a small `<style>` in the report if a one-off tweak is needed. |
| `assets/themes/<name>/theme.json` | The theme's fonts and running header/footer style, read by `build.py`. |
| `assets/template.html` | Every component with placeholder text. Copy the parts you need. |
| `assets/fonts/` | Bundled static TTFs for both themes (Manrope, Source Sans 3, Source Serif 4 italic, Inter, JetBrains Mono) with their OFL licenses. |
| `scripts/build.py` | Injects theme + fonts and writes standalone HTML and/or renders PDF. |
| `references/components.md` | Markup, class names and palette for each component. |
| `examples/example.*`, `examples/example-minimal.*` | The template built in each theme. |

## Workflow

1. **Get the content** (the user's file, text, or an existing document). Work out its structure as it is: parts → sections → subsections. Don't restructure it.
2. **Pick the theme** (see Themes above).
3. **Start from `assets/template.html`.** Keep `<!-- THEME -->`, set `<title>`, `<meta name="doc-short">` (top-right running head) and `<meta name="doc-footer">` (bottom-left footer) from the user's document title. Delete placeholder components that the content does not use.
4. **Pour the content into the components** in `references/components.md`, preserving the text exactly (escape `<`, `>`, `&`). Give each part its colour class `c-blue, c-teal, c-violet, c-green, c-amber, c-rose, c-indigo, c-plum, c-forest, c-slate` in order, on the part divider, its sections and its contents entry.
   - Short document (1–4 pages): skip the contents page and part dividers; use a title block plus `.chapter` sections.
5. **Build:**
   ```bash
   python3 <skill>/scripts/build.py report.html --theme minimal --html out.html --pdf out.pdf
   ```
   - `--fonts google` (default for HTML) or `--fonts embed` for a fully offline single file (~2.7 MB).
   - PDF engine: `weasyprint` (default, full support) or `--engine chrome` (no running section title, no contents/cross-reference page numbers). Install with `brew install weasyprint` or `pip install weasyprint`.
   - Never overwrite the source file with built output.
6. **Verify visually.** Render pages to PNG and look at them (`pdftoppm -r 60 -png out.pdf <dir>/p`):
   cover fits on one page; part dividers fill their page (dark in `manual`, tinted in `minimal`); contents page numbers are filled; no SVG shapes render black; no overflow in panels; no heading stranded at the bottom of a page; no emoji anywhere. For HTML, check desktop and phone width.
7. Tell the user where the files are and which theme was used.

## Look rules

- Each theme's palette and typography are fixed (see `references/components.md`); don't mix them. Don't add colour backgrounds to body text, shadows or gradients; the style is flat and hairline-ruled.
- In inline SVG, set colours with the kit classes or literal hex in `style="fill:#…"`; never `var(--…)` (PDF engines ignore it). `build.py` copies the SVG kit styles into each `<svg class="diagram">`.
