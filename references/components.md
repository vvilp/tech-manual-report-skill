# Component reference

All markup lives inside `<body class="manual">`. `assets/template.html` shows every piece in context.

## Palette

| Token | Hex | Use |
|---|---|---|
| paper | `#faf8f3` | page background |
| panel | `#f4f2ea` | figures, code, takeaways |
| line / rule | `#e0ddd0` / `#b9b6a6` | hairlines / heavy rules |
| ink / muted / faint | `#161d27` / `#5f6772` / `#878e97` | text levels |
| code-ink | `#24405e` | inline code |
| night | `#0e1826` | part divider pages |

Part colors (in order): blue `#2a5f88`, teal `#10707a`, violet `#5c4a8c`, green `#0d6b4f`, amber `#8a5a18`, rose `#97405a`, indigo `#3d4f96`, plum `#7a3f78`, forest `#2f5d46`, slate `#4a525c`.

Diagram tones `t-<name>` (fill / stroke): blue, teal, violet, indigo, amber, green, olive, rose, plum, gray. Semantic habit from the reference: blue = data/records, amber = tasks/work, violet = intake/queues, indigo = observers/views, teal = storage/kernel, green/olive = environment/effects, rose = errors/failures/interrupts, gray = host/neutral, hatched = pending/inferred.

## Page-level structure

### Cover
```html
<section class="cover">
  <div class="cover-top">
    <div class="brand"><span class="brand-mark"><svg …/></span>Product Name</div>
    <div class="cover-meta">Technical Manual<br><strong>pkg 1.0.3 · Engineering Edition · 2026.10</strong></div>
  </div>
  <div class="plate-bar"><span>Plate I · What the picture shows</span><span>Right-hand note</span></div>
  <div class="plate">
    <div class="plate-grid"> <svg class="diagram">…</svg> <div><div class="label">Key</div><ol class="key">…</ol></div> </div>
    <div class="mini-figs"> <div><div class="mini-head">Fig. 2 · Name</div>…<div class="mini-cap">One line.</div></div> ×4 </div>
  </div>
  <div class="cover-title">
    <h1>Product Name</h1>
    <div class="subtitle">Technical Manual</div>
    <p class="lede">One-paragraph scope statement.</p>
    <div class="legend"><span style="--dot:var(--c-blue)">Model</span> …one per part</div>
  </div>
</section>
```
Key item: `<li><span class="step">1</span><b>Commit seq</b><i>one atomic commit per tick</i></li>`.

### Contents
```html
<nav class="toc">
  <h1>Contents</h1>
  <div class="toc-part c-blue">
    <div class="toc-part-title"><span class="num">1</span>The Model</div>
    <ol><li><a href="#s-1-1"><span class="n">1.1</span><span class="t">Title</span><span class="dots"></span></a></li></ol>
  </div>
</nav>
```
Page numbers are generated in the PDF from the `href`; every `href` must match a section `id`.

### Part divider
```html
<section class="part c-teal" id="part-2">
  <div class="part-inner">
    <div class="part-label">Part 2</div>
    <h1>Sessions and Commits</h1>
    <p class="dek">One-sentence italic thesis of the part.</p>
    <div class="part-rule"></div>
    <ol><li><a href="#s-2-1"><span class="n">2.1</span><span class="t">Records and IDs</span></a></li></ol>
  </div>
  <div class="part-numeral">02</div>
  <div class="part-foot"><span class="doc"></span><span>Part 2</span></div>
</section>
```

### Section
```html
<section class="chapter c-teal" id="s-2-1">
  <header class="sec-head">
    <div class="sec-num">2.1</div>
    <h1>Records and IDs</h1>
    <p class="dek">Italic one- or two-sentence summary.</p>
  </header>
  … body …
</section>
```
Every `.chapter` starts a new PDF page; add class `continue` to let one flow on. The `h1` text becomes the running head (top-left).

Front-matter pages (e.g. "How to read this") can be a `.chapter` with `sec-num` `00`.

## Body components

| Need | Markup |
|---|---|
| Inline code | `<code>Storage.commit()</code>` |
| Source citation | `<cite>spec §4</cite>` / `<cite>src/session.ts</cite>` |
| Cross-ref | `<a class="xref" href="#s-2-3">when a commit fails</a>` → PDF adds `(p. 33)` |
| Defined term | `<span class="term">mutation line</span>` or `<b>` |
| Term — explanation list | `<div class="defs"><p><b>Storage</b> — text…</p>…</div>` |
| Warning callout (rose) | `<div class="callout warn"><span class="label">Experimental</span><p>…</p></div>` |
| Rule / quote callout (blue) | `.callout.rule` with label `Core rule` |
| Tip (green) / Note (amber) | `.callout.tip` / `.callout.note` |
| Summary box | `<div class="takeaways"><span class="label">What this means for you</span><ul><li>…</li></ul></div>` |
| Sources line | `<div class="sources"><b>Sources:</b> docs/spec.md (§1, §4); src/…</div>` |
| Table | plain `<table><thead>…</thead><tbody>…</tbody></table>`; `.compact` for reference tables; caption after with `<p class="table-caption">` |
| Code block | `<div class="code"><div class="code-head">Title<span class="path">file.ts</span><span class="lang">TS</span></div><pre>…</pre></div>` then optional `<p class="code-note">` |
| Token colours (optional) | `tk-k` keyword, `tk-s` string, `tk-n` number, `tk-c` comment, `tk-f` function |
| KPI row | `<div class="kpis"><div class="kpi"><div class="v">99.9%</div><div class="k">Uptime</div></div>…</div>` |
| Quote | `<blockquote>` (serif italic) |
| Chips / steps / tags | `<span class="chip t-blue">13</span>`, `<span class="step">3</span>`, `<span class="tag">SIGKILL</span>` |

Escape `<`, `>`, `&` inside `<pre>`.

## Figures

```html
<figure class="fig">
  <figcaption class="fig-head"><span class="no">Fig. 1.2</span><span class="title">The layers of a harness</span><span class="kind">Layers</span></figcaption>
  …diagram…
</figure>
<p class="caption"><b>Bold first sentence states the finding.</b> Grey detail and provenance.</p>
```
`kind` is a one-word type tag: LAYERS, FLOW, SEQUENCE, COMPARISON, TIMELINE, STATE, SCHEMA.

### HTML diagrams (boxes, layers, grids)
- `.lane` — mono uppercase lane label above a row.
- `.row` — horizontal flex row of equal children; `.stack` — vertical.
- `.group` — white rounded container (dark outline) grouping nodes; `.group.soft` — hairline.
- `.node` + tone: `<div class="node t-amber"><b>Task scheduler</b><small>reserves and runs</small></div>`.
  Modifiers: `.mono` (mono title), `.white`, `.hatch` (pending/inferred), `.dashed`, `.left`, `.strong`.
- `.flow-arrow` — a `→` between nodes in a row.

### SVG diagrams (arrows, sequences, timelines)
Use `<svg class="diagram" viewBox="0 0 640 H">` (width ≈ 640 units matches the text column). Kit classes:
- shapes: `rect.box` + tone `blue|teal|violet|indigo|amber|green|olive|rose|plum|white`; `rx="2"`.
- lines: `.wire` (+ `teal|amber|rose|plum`), `.dash`, `.life` (dotted lifeline).
- text: default 12px ink; `.mono`; `.lbl` (mono uppercase 10px faint); `.sub` (10.5px muted); `.it` (serif italic); colour `.t-blue|t-teal|t-amber|t-rose|t-plum|t-muted`.
- arrowheads: define a `<marker>` per colour in `<defs>` (see template).
- Override fill on one element with `style="fill:#hex"` (inline style beats the class). Never `var(--…)` in SVG.
- Step numbers: `<circle r="8" fill="none" stroke="#161d27"/>` + centred mono text size 9.

Sequence diagram recipe: actor boxes across the top (y≈6, h≈32) with `.lbl` names, `.life` lines down, horizontal `.wire` messages with mono labels above and `.sub` notes below, circled step numbers in the left gutter. Use teal for writes to storage, amber dashed for scheduler/reservations, plum for model/external calls, rose for failures.
