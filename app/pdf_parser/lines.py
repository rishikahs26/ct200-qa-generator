import re
import pdfplumber

HEADING_RE = re.compile(r'^(\d+(?:\.\d+)*)\.?\s+(\S.*)$')

def _join_with_hyphen_fix(line_words):
    """Fix PDF font-substitution bug where non-breaking hyphens get
    extracted as separate glyph runs (e.g. 'CT-200' -> 'CT', '‑', '200')."""
    parts = []
    for w in line_words:
        text = w['text']
        if text in ('‑', '-') and parts:
            parts[-1] = parts[-1] + text
            continue
        if parts and parts[-1].endswith(('-', '‑')):
            parts[-1] = parts[-1] + text
            continue
        parts.append(text)
    return ' '.join(parts)


def _group_into_lines(words, tolerance=2.0):
    lines = []
    current = []
    current_top = None
    for w in sorted(words, key=lambda w: (w['top'], w['x0'])):
        if current_top is None or abs(w['top'] - current_top) <= tolerance:
            current.append(w)
            current_top = w['top'] if current_top is None else current_top
        else:
            lines.append(current)
            current = [w]
            current_top = w['top']
    if current:
        lines.append(current)
    return lines


def extract_lines(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=['size', 'fontname'])
            if not words:
                continue
            for line_words in _group_into_lines(words):
                text = _join_with_hyphen_fix(line_words)
                size = max(w['size'] for w in line_words)
                bold = any('Bold' in w['fontname'] for w in line_words)
                lines.append({
                    'text': text,
                    'size': round(size, 1),
                    'bold': bold,
                    'page': page_num,
                    'top': line_words[0]['top'],
                })
    return lines


def classify_line(line):
    """Returns (kind, number, text). kind is 'heading' or 'body'.
    Numbering pattern is the PRIMARY signal, not font size, because
    the deepest heading (2.1.1.1) shares its font size with bold body
    text and table headers."""
    m = HEADING_RE.match(line['text'])
    if m and line['bold']:
        return 'heading', m.group(1), m.group(2)
    return 'body', None, line['text']