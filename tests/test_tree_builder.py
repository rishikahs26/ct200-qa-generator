from app.pdf_parser.lines import extract_lines, classify_line
from app.pdf_parser.tree_builder import build_tree, flatten

V1 = 'data/ct200_manual.pdf'


def _tree():
    lines = extract_lines(V1)
    classified = [classify_line(l) for l in lines]
    return build_tree(classified)


def test_deep_node_parent_is_2_1_not_2_or_2_1_1():
    node = [n for n in flatten(_tree()) if n.number == '2.1.1.1'][0]
    assert node.parent.number == '2.1'


def test_section_3_children_sorted_numerically():
    section3 = [n for n in flatten(_tree()) if n.number == '3'][0]
    child_numbers = [c.number for c in section3.children]
    assert child_numbers == ['3.1', '3.2', '3.3', '3.4']


def test_section_8_single_child_tree_is_fine():
    section8 = [n for n in flatten(_tree()) if n.number == '8'][0]
    assert len(section8.children) == 1
    assert section8.children[0].number == '8.1'