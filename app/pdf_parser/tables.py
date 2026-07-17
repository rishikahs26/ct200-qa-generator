def extract_clean_tables(page):
    """pdfplumber sometimes detects the same table twice: once correctly,
    once as word-fragments (e.g. ['0-', '299', 'mmHg'] instead of
    ['Pressure range', '0-299 mmHg']). Keep only tables with a sane,
    consistent column count and no empty cells."""
    raw_tables = page.extract_tables()
    clean = []
    for t in raw_tables:
        if not t:
            continue
        col_count = len(t[0])
        rows = [r for r in t if len(r) == col_count and all(c and c.strip() for c in r)]
        if len(rows) >= 2:
            clean.append(rows)
    return clean[0] if clean else None