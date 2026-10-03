# 打印后手写批注：print

Use a left-bound double-sided A4 study book. Logical body page 1 is a right-hand recto. Coordinates are millimetres from the top-left; A4 is 210 × 297.

| Area | Odd body page | Even body page |
| --- | --- | --- |
| Blank inner binding margin | x = 0–20, left | x = 190–210, right |
| Central body, width 128 | x = 20–148 | x = 62–190 |
| Gap, width 5 | x = 148–153 | x = 57–62 |
| Merged annotation column, width 45 | x = 153–198, right | x = 12–57, left |
| Outer margin, width 12 | x = 198–210 | x = 0–12 |
| Page-number alignment | x = 198, y = 291, right aligned | x = 12, y = 291, left aligned |

Merge the former two sidebars into one outer column. Use the continuous outer column as a second teaching channel and writing area. Allocate notes, comparisons and diagrams by their anchors; assess free space over the chapter, not a fixed fraction on every page. Match annotation and page-number sides.

Keep the complete 20 mm inner margin blank, including rules, backgrounds, bars, figures and running labels. Mirror the body as well as the annotation column. Use a subtle divider at x = 150.5 on odd pages and x = 59.5 on even pages.

Use `Resources/templates/print-master.pdf` and the exact rows and field positions in `template-manifest.json`. Reserve an independent pale green joke/trivia/quotation strip at the physical bottom of the page; all body grid slots must end above it. Use the shared baseline grid, currently about 7.2 mm per row, with each body baseline about 1 mm above its rule. Start blocks on designated rows and allocate whole-row heights. Clear blue rules must remain visible at ordinary reading size. Do not reuse the former independent 5.2 mm decorative ruling.

Use dedicated full-width odd/even masters for the multi-level contents and the final chapter-grouped specialist glossary. Both preserve the 20 mm inner binding margin and outer page-number side. Contents entries come from the independent outline rather than page titles; glossary entries contain only English terms and concise Chinese meanings. Ordinary teaching pages return to the central body plus outer annotation column.

Only chapter-opening masters include the full black chapter heading and green or yellow-green section stroke. Keep the opening within the 178 mm content span, starting at x = 20 odd / 12 even, at the manifest-defined opening position below the running header. Continuation masters restore the former chapter-title area to usable rows. Follow the series title hierarchy without a large solid green title block.

Use a short actual-subject running header. Place a short joke, interesting fact, subject fact or attributed quotation selected without repetition from the bundled corpus in the independent pale green strip at the physical page bottom, with one or at most two dark text lines. The strip is fixed page furniture outside the body grid, never a top strip or a concluding knowledge section/body block. The strip starts at y = 275 mm and is 10 mm high, with `#F3F7E0` background and `#252823` text. Preserve the blank 20 mm binding margin and keep page numbering clear of its text, normally at baseline y = 291 mm; exact field positions come from the template manifest. Use the picker described in [Short fun content](fun-content.md); count attribution within the two-line limit.

Allow wide tables to span 178 mm if needed, retaining the binding margin. Resume the normal annotation layout on the next ordinary page.

## Cover parity

Keep body page 1 on the right when a separately drawn cover with blank reverse precedes it. Include a subject front cover for a whole-book request; do not add one to a chapter or sample unless requested. If a PDF includes a cover, include its blank reverse or correctly paired front matter so logical odd body pages still print on the right. Count physical pages separately from displayed body numbers and verify the duplex sequence.

Active master: `Resources/templates/print-master.pdf`. Filled example: `Resources/examples/print-reference.pdf`.

## Active visual rules

Use `series-contract.md` and `visual-system.md` for current paper, hierarchy, connected complete teaching sections, handwritten notes and source-referenced sidebar comics. The older reference PDF demonstrates geometry only. Put a black chapter heading and a brush-like section strip within the opening title area; do not require the old oversized white chapter digit on a solid green block. Preserve ordinary-page coordinates. A wider teaching spread may vary internal composition while retaining usable annotation areas and the edition's binding rules.

## Ink-saving paper

Use pure white paper without a full-page background fill. Leave blank writing and binding areas unpainted. Retain clear baseline-aligned blue rules and selective teaching highlights; avoid large tinted panels. Apply the same ink-saving principle to the print cover: preserve series composition using coloured accents on white rather than a solid coloured page.
