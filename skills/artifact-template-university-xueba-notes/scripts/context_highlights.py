"""Render editorially selected paragraph spans without choosing their importance.

Authors select a passage in its particular context and supply ``highlights`` as
``{start, end, text, reason}`` objects. Offsets are zero-based Unicode code-point
positions in ``pdf_template_layout.clean(paragraph_text)``; ``end`` is exclusive.
``text`` must equal that exact slice. ``reason`` records the editorial decision
and is never printed. No keyword list, occurrence search or automatic selection
is used here. A repeated phrase stays plain unless its own occurrence is marked.

``validate_content_highlights(content)`` checks an entire content object before
rendering. ``contextual_highlight_lines(text, lines, highlights)`` maps explicit
spans onto the existing wrapper's lines and returns ``(line, fragments)`` pairs;
each fragment is a pair of character offsets relative to that rendered line.
Only whitespace discarded by the wrapper may be skipped during this mapping.
"""
from pdf_template_layout import clean


def validate_highlights(text, highlights, location='paragraph'):
    """Return sorted, validated local spans; never infer spans from their text."""
    source = clean(text)
    if not isinstance(highlights, list):
        raise ValueError(f'{location}.highlights must be a list of explicit local spans')
    spans = []
    for index, item in enumerate(highlights):
        label = f'{location}.highlights[{index}]'
        if not isinstance(item, dict):
            raise ValueError(f'{label} must contain start, end, text and reason')
        start, end = item.get('start'), item.get('end')
        if type(start) is not int or type(end) is not int:
            raise ValueError(f'{label}: start and end must be integer Unicode code-point offsets')
        if not 0 <= start < end <= len(source):
            raise ValueError(f'{label}: offsets must identify a nonempty slice of clean(paragraph text)')
        if item.get('text') != source[start:end] or not source[start:end].strip():
            raise ValueError(f'{label}: text must match the exact nonblank slice at start:end; review the span after editing the paragraph')
        if not isinstance(item.get('reason'), str) or not item['reason'].strip():
            raise ValueError(f'{label}: reason must explain why this passage matters in this context')
        spans.append((start, end))
    spans.sort()
    if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
        raise ValueError(f'{location}.highlights contains overlapping spans; consolidate the editorial selection')
    return spans


def validate_content_highlights(content):
    """Reject legacy global emphasis and validate paragraph-local selections."""
    if content.get('emphasis'):
        raise ValueError(
            'Global emphasis keyword lists are no longer supported. Review each '
            'paragraph in context, remove top-level emphasis, and author local '
            'paragraph.highlights with start, end, text and a contextual reason.'
        )

    def visit(value, location):
        if isinstance(value, dict):
            if 'highlights' in value:
                if value.get('type') not in {'paragraph','definition','property','rule','condition','example_inline','common_error','memory_note','diagram_explanation','method_card'}:
                    raise ValueError(f'{location}: highlights require a text-bearing knowledge block')
                if not isinstance(value.get('text'), str):
                    raise ValueError(f'{location}: highlighted paragraphs require text')
                validate_highlights(value['text'], value['highlights'], location)
            for key, child in value.items():
                visit(child, f'{location}.{key}')
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f'{location}[{index}]')

    visit(content, 'content')


def contextual_highlight_lines(text, lines, highlights):
    """Map authored spans through wrapping, including selections crossing lines."""
    source = clean(text)
    spans = validate_highlights(text, highlights)
    cursor = 0
    mapped = []
    for rendered in lines:
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
        end = cursor + len(rendered)
        if source[cursor:end] != rendered:
            raise ValueError('Wrapped text no longer maps to the paragraph; update the span mapper with the wrapping rule')
        fragments = [
            (max(start, cursor) - cursor, min(stop, end) - cursor)
            for start, stop in spans if start < end and stop > cursor
        ]
        mapped.append((rendered, fragments))
        cursor = end
    if source[cursor:].strip():
        raise ValueError('Wrapped text omitted non-whitespace paragraph content')
    return mapped
