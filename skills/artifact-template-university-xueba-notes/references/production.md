# Production workflow

## References and priority

Retain the original `assets/reference.docx`, `assets/preview.png`, `assets/icon.svg` and `artifact-template.json`. They preserve the template's visual origin. The current instructions and selected layout reference control the requested changes to margins, chapter openings, continuation pages, running labels and short footers.

Inspect the selected PDF in `assets/examples/`. Both references contain 14 pages: eight specification pages and six continuous asymptotic-analysis pages with expanded terminology, generated illustrations, full English examples and Q1–Q4 with complete answers. These are concrete demonstrations rather than a course manuscript to relabel.

## Build and adapt

Use the Documents skill for editable DOCX and the PDF skill for precisely paginated PDFs. Preserve the colour and typography hierarchy while applying the selected geometry. Keep content independent of pagination when generating both editions.

The bundled `scripts/build_reference.py` reproduces the reference PDFs. Adapt its drawing primitives or replace its demonstration content with a source-grounded course manuscript; generate new subject-specific illustration assets as needed.

```sh
python scripts/build_reference.py --edition print --font-dir /path/to/fonts --output print-reference.pdf
python scripts/build_reference.py --edition digital --font-dir /path/to/fonts --output digital-reference.pdf
```

Install ReportLab, Pillow and fontTools as needed. Use `scripts/prepare_fonts.py --output-dir /path/to/fonts` to obtain the licensed reference fonts, or supply existing `WenKai.ttf`, `Sans.ttf`, `SansBold.ttf` and named DejaVu fonts. Keep licences next to downloaded fonts. Check every needed course glyph before final production.

The builder writes a neighbouring `<output-stem>.layout.json` with geometry, annotation blocks and footer line counts. Keep production metadata outside the course pages.

## Verification

Rebuild both modes after layout edits, then run:

```sh
python scripts/verify_reference.py print-reference.pdf --edition print
python scripts/verify_reference.py digital-reference.pdf --edition digital
```

Render all pages to PNG and visually inspect them. Check chapter digits and title strips only on chapter openings, continuation starts at y = 16, footer maximum two lines, formulas, English wrapping, complete answers and transparent sharp illustrations.

For print pages require one outer annotation column and one writing label, matched with the page number, and fully blank 20 mm inner margins. For digital pages require two fixed columns, two writing labels and free writing space on both sides. Inspect the densest annotation pages in both editions, and verify cover parity where relevant.
