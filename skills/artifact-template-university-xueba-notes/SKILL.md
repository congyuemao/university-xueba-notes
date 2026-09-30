---
name: artifact-template-university-xueba-notes
description: "Create a complete rereadable university study book using the 大学学霸笔记 University Xueba Notes template and retained reference. Use when the user selects this template or personal skill, names 大学学霸笔记, or asks to turn courses, lectures, textbooks or a syllabus into substantial knowledge notes with annotation margins, generated illustrations, expanded bilingual terminology, full English worked solutions and answered self-tests. Offer a print edition with mirrored outer annotations or a digital edition with two annotation columns. Keep the central knowledge text complete rather than reducing it to a cheat sheet or flashcards."
---

# 大学学霸笔记 University Xueba Notes

Create a coherent university study book that the learner can read from beginning to end repeatedly. Use continuous foundational explanations, precise conditions, useful illustrations and complete worked applications.

## Select the writing medium first

Resolve the edition from the user's current request and previous choice. Recognise printing, binding, paper and handwritten paper notes as `print`; recognise computer, tablet, stylus, PDF annotation and electronic reading as `digital`. Keep that choice across chapter batches.

When the medium is unspecified, ask once before final pagination:

**“你准备怎样使用这份笔记？”**

1. **“打印后手写批注”** — generate `print`: one merged outer annotation column; odd pages right, even pages left; blank inner binding margin.
2. **“在电脑或平板上批注”** — generate `digital`: central body with separate left and right annotation columns on every page.

Use the available choice UI when suitable; otherwise ask the same concise question in text. Do not mark either edition as universally better. If the user requests both, prepare one knowledge manuscript and paginate two named files. If no answer arrives and work must continue, state the assumption and default to `print`. Continue source reading and drafting while waiting for an optional answer.

Read the selected [print layout](references/layout-print.md) or [digital layout](references/layout-digital.md). For either edition read [shared editorial rules](references/content-and-language.md), [illustration 103 prompts](references/illustration-103.md) and [production workflow](references/production.md).

## Use the retained template

1. Read `artifact-template.json`; resolve its paths relative to this directory.
2. Open the available Documents or PDF capability and follow its authoring, rendering and verification workflow. Use `assets/reference.docx` as the retained visual source, with the chosen layout reference and this skill's current rules controlling the requested changes.
3. Keep the original DOCX, preview and manifest intact. Inspect `assets/examples/print-reference.pdf` or `assets/examples/digital-reference.pdf` for the updated layout.
4. Read the supplied syllabus, slides, textbooks, tutorials and examination material sufficiently to map the complete topic sequence and prerequisites. Use them as the primary content sources.
5. Create a stable chapter plan and bilingual terminology system. For a whole-course request cover every supplied syllabus topic; use volumes or chapter batches when needed, preserving one coverage map and consistent numbering.
6. Write and paginate the central manuscript, then place teaching annotations, generated illustrations and generous empty writing areas in the chosen margins.
7. Render every output page, inspect its image, fix defects and repeat affected checks before delivery.

## Build a complete knowledge text

For each concept include its motivating question, definition, notation, conditions, intuitive explanation and canonical example. Add derivation, proof, causal reasoning, algorithmic steps, representative applications, counterexamples and connections where the discipline requires them. A learner who has forgotten the prerequisites must be able to restart from the central text.

Keep core facts in the central manuscript. Use sidebars to reinforce prerequisites, terminology, misconceptions and connections. Keep symbols, names and translations stable. Reintroduce necessary foundations where later chapters depend on them. End each chapter with readable “基础知识再读” prose that restores the knowledge relationships.

Spend substantial space on foundations. A useful balance is 55–70% explanation, 20–30% worked applications, and 10–15% extensions, adjusted to the course. Use lists, tables and coloured callouts to support connected prose. Do not replace the book with disconnected boxes or recall cards.

## Support English examinations

Use Chinese explanations with standard English terminology unless the user specifies another policy. Expand each core terminology entry beyond translation: English name and abbreviation, Chinese meaning, a full English definition with conditions, related-concept explanation, and an English examination sentence. Aim for 6–12 substantial entries per core theme when useful. Put long entries in central terminology sections and add a book-wide index.

Write the complete problem statement and complete worked solution in English. Include the method, intermediate steps, reasons, result and interpretation. Put optional Chinese intuition before or after the full English solution. Retain proof quantifiers, calculation substitution and units, and relevant algorithmic correctness, termination and complexity reasoning.

Attach a complete answer to **every self-test question and every subquestion**, including “闭书回忆”. Match identifiers exactly; include definitions, evidence, intermediate reasoning and final results. Answers may follow immediately or appear in a clearly referenced chapter answer section. Use English answers for an English examination. Never deliver an unanswered recall prompt.

## Apply recurring page rules

- Use A4 portrait, pale ruled lines, green chapter accents, blue knowledge numbering and selective yellow highlighting. Preserve the reference's textbook feel and handwritten Chinese typography where available.
- Show the large chapter number, title and long green bar only when a new chapter begins. Increment by chapter, not by page.
- Remove the entire title block on continuation pages; extend the body and annotation regions upwards into its former space. Keep appropriate blank space wherever there is no new content.
- Use the actual subject in the page header and optional footer, or omit the running label. Remove generic “大学学霸笔记” and “大学学霸笔记 教辅出版物范式” branding from course-page running labels.
- Alternate page numbers: odd right, even left. In `print`, put the merged annotation column on the same outer side. In `digital`, keep both annotation columns fixed.
- Put one short quotation, trivia item or joke at the bottom of **every content page**. Prefer one line; allow at most two including attribution, in a strip about 10 mm high. Any suitable subject is allowed, including material unrelated to the course. Verify quotes and facts; keep jokes concise.
- Leave about half or more of the annotation area free across a chapter. Reserve the print binding margin completely. Do not fill writing space merely because it is available.

## Generate and embed illustrations

Use the image-generation capability to make hand-drawn concept illustrations, then embed the resulting asset. Use handraw-style entry **103**, **Minimal Absurd Short-Gag Cartoon**, with the original Chinese traits and bilingual prompts in [illustration-103.md](references/illustration-103.md). Request a transparent background for cutout illustrations.

Choose one teachable idea per illustration and typeset its labels, dialogue and formulas separately. Use exact native drawing or typesetting for diagrams whose geometry or numerical relationships must be precise. Preserve the meaning of supplied course figures. The bundled `assets/illustrations/asymptotic-upper-bound.png` is an existing generated example; create subject-specific assets when a new concept requires them.

## Write direct learning prose

Explain knowledge, conditions, reasoning and applications directly. Keep defensive disclaimers, AI meta-commentary, process assurances and production notes out of the study book. Put subject-relevant assumptions and genuine boundary conditions alongside their definition or conclusion.

Use sources faithfully, preserve named results and notation, and resolve factual conflicts. Collect books, papers and external sources in a readable references section. Omit specific teacher-PPT page numbers from the learner-facing pages.

## Check before delivery

Confirm that the central text teaches foundations fully and reads coherently on repeated passes; every example has a full English solution; every self-test subquestion has a complete answer; expanded terminology includes definitions and use; chapter starts and continuation pages follow the shared rules; every content page has a one- or two-line footer; illustrations are generated and embedded; and the chosen geometry leaves usable writing space.

Inspect all rendered pages for clipping, overlapping annotations, broken formulas, unreadable English wrapping, excessive footers and crowded margins. For `print`, verify odd/right and even/left annotations and page numbers, blank 20 mm inner margins, and cover parity. For `digital`, verify two separate annotation areas on every page and no mirrored binding offset.

Deliver the requested edition with the subject and edition in the filename. When both are requested, return clearly labelled print and digital files containing the same knowledge and answers.
