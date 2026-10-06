---
name: tech-manual-report
description: Create HTML and/or PDF reports in the "Technical Manual" house style (modeled on the Pi Durable Technical Manual) — warm paper background, navy ink, Manrope headings, Source Serif italic deks, JetBrains Mono letterspaced labels, dark part-divider pages with giant numerals, numbered sections, FIG.-labelled diagram panels, callouts, "What this means for you" boxes, and Sources lines. Use when the user asks for a report, manual, handbook, technical write-up, design doc, whitepaper or explainer "in the technical manual style / like the Pi Durable PDF", or asks for a polished HTML or PDF report with this theme.
---

# Technical Manual report

Produces a report that looks like the Pi Durable Technical Manual: one themed HTML source that renders as a scrolling web page **and** as a paginated US‑Letter PDF with running headers, page numbers, a contents page with real page numbers, and `(p. 33)` cross‑references.

## Files

| Path | What it is |
|---|---|
| `assets/template.html` | Complete worked example using every component. **Copy it as your starting point.** |
| `assets/theme.css` | The theme (screen + `@media print` + `@page`). Do not inline-edit per report; override in a small `<style>` if needed. |
| `assets/fonts/` | Bundled static TTFs (Manrope, Source Sans 3, Source Serif 4 italic, JetBrains Mono). |
| `scripts/build.py` | Injects theme + fonts, writes standalone HTML and/or renders PDF. |
| `references/components.md` | Markup for every component, palette, and diagram rules. Read it before writing content. |
| `examples/example.pdf`, `examples/example.html` | The template, built. Look at these to see the target output. |

## Workflow

1. **Gather content.** Know the subject, audience, and the parts/sections before writing markup. A manual reads best as Parts (2–10) → numbered sections (`1.1`, `1.2`…) → `h2`/`h3`.
2. **Copy the template** to the working location (e.g. `report/report.html`) and replace the example content. Keep the structure:
   `cover` → `nav.toc` → for each part: `section.part.c-<color>` then its `section.chapter.c-<color>` sections.
3. **Set the metadata** in `<head>`: `<title>`, `<meta name="doc-short">` (top‑right running head) and `<meta name="doc-footer">` (bottom‑left footer, printed in caps). Leave the `<!-- THEME -->` marker in place.
4. **Write the content** with the components in `references/components.md`. Writing style that matches the reference:
   - Each section opens with a one‑sentence italic **dek** that states the section's point.
   - Short, plain declarative sentences. Bold the term being defined the first time (`<span class="term">`).
   - Back claims with `<cite>` source tags (`spec §4`, `src/x.ts`) and end each section with a `.sources` line when there are sources.
   - Close a major section with a `.takeaways` "What this means for you" box (3–5 bullets).
   - Number figures per section (`Fig. 2.3`) and give each a caption whose first sentence is bold and states the finding.
   - Cross‑reference other sections with `<a class="xref" href="#s-2-3">…</a>`; the PDF appends `(p. N)`.
5. **Build:**
   ```bash
   python3 <skill>/scripts/build.py report.html --html report-out.html --pdf report.pdf
   ```
   - `--fonts google` (default for HTML): small file, fonts from Google Fonts. `--fonts embed`: fully offline single file (~2.6 MB).
   - PDF engine: `weasyprint` (default; full support) or `--engine chrome` (no running section titles, no TOC/xref page numbers). If WeasyPrint is missing: `brew install weasyprint` or `pip install weasyprint`.
   - Never write the built output over the source file; the source keeps the `<!-- THEME -->` marker.
6. **Verify visually — always.** Render pages to PNG and look at them:
   ```bash
   pdftoppm -r 60 -png report.pdf /tmp/pages/p      # then Read a few PNGs
   ```
   Check: cover fits on one page; part dividers are full dark pages; no figure/table split awkwardly; TOC numbers are filled; no SVG boxes rendered black; no text overflowing figure panels. For HTML, open/screenshot at desktop and phone width.
7. Tell the user where the HTML/PDF files are. Offer to publish the HTML if they want a shareable link.

## Rules that keep the look right

- **Palette is fixed.** Use the part colors `c-blue, c-teal, c-violet, c-green, c-amber, c-rose, c-indigo, c-plum, c-forest, c-slate` in that order for parts 1..10, and put the same class on the part's chapter sections and its `.toc-part`. Node tones (`t-blue`, `t-amber`, …) are for diagrams only.
- **Typography is fixed**: Manrope for headings, Source Sans 3 for body, Source Serif 4 *italic only* for deks/captions in plates, JetBrains Mono for labels, code, citations, numbers. Labels are uppercase with wide letterspacing (`.label`).
- **Diagrams**: prefer HTML blocks (`.fig` + `.lane` + `.row` + `.node`) for layered/box diagrams; use inline `<svg class="diagram">` with the kit classes for anything with arrows, timelines or sequences. In SVG, put colours on elements via kit classes or literal hex in `style="fill:#…"`; never `var(--…)` inside SVG (PDF engines ignore it). build.py copies the SVG kit styles into each diagram automatically.
- The cover "plate" is optional but is the signature of the style: a hero diagram + a numbered KEY column + a strip of 2–4 mini figures. If there is nothing meaningful to draw, use a KPI row or a simple layered `.fig` instead — don't draw decoration.
- Keep body sections `max-width` as given; don't add colored backgrounds to body text, emojis, drop shadows, or gradients. The style is flat, hairline-ruled and quiet.
- For a short report (1–4 pages) drop the TOC and part dividers: cover (or just a section header) + chapters. For one‑section HTML-only output, the `.chapter` alone looks right.
