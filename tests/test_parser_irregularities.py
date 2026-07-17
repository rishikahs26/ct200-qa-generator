from app.pdf_parser.lines import extract_lines, classify_line

V1 = 'data/ct200_manual.pdf'


def test_hyphenated_words_are_not_mangled():
    lines = extract_lines(V1)
    text = ' '.join(l['text'] for l in lines)
    assert 'CT-200' in text or 'CT‑200' in text


def test_deep_heading_2111_is_detected_as_heading():
    lines = extract_lines(V1)
    kinds = [classify_line(l) for l in lines]
    matches = [k for k in kinds if k[0] == 'heading' and k[1] == '2.1.1.1']
    assert len(matches) == 1
    assert 'Battery Life' in matches[0][2]


def test_table_header_row_is_not_classified_as_heading():
    lines = extract_lines(V1)
    kinds = [classify_line(l) for l in lines]
    for kind, number, text in kinds:
        assert not (kind == 'heading' and text.strip() == 'Value')


def test_classification_list_is_not_classified_as_headings():
    # "1. Normal: systolic < 120..." under 3.3 must NOT be treated as a heading
    lines = extract_lines(V1)
    kinds = [classify_line(l) for l in lines]
    for kind, number, text in kinds:
        if text.startswith('1. Normal'):
            assert kind == 'body'


def test_headings_out_of_pdf_order_are_all_found():
    lines = extract_lines(V1)
    kinds = [classify_line(l) for l in lines]
    numbers = [n for k, n, t in kinds if k == 'heading']
    for expected in ['3.1', '3.2', '3.3', '3.4']:
        assert expected in numbers

def test_top_level_heading_with_trailing_period_is_detected():
    lines = extract_lines(V1)
    kinds = [classify_line(l) for l in lines]
    matches = [k for k in kinds if k[0] == 'heading' and k[1] == '1']
    assert len(matches) == 1
    assert matches[0][2] == 'Device Overview'