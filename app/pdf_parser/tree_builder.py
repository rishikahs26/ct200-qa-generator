import hashlib


class Node:
    def __init__(self, number, heading, level, parent=None):
        self.number = number
        self.stable_key = number
        self.heading = heading
        self.level = level
        self.parent = parent
        self.children = []
        self.body_lines = []

    @property
    def body_text(self):
        return '\n'.join(self.body_lines).strip()

    @property
    def content_hash(self):
        return hashlib.sha256(self.body_text.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            'number': self.number,
            'heading': self.heading,
            'level': self.level,
            'body_text': self.body_text,
            'content_hash': self.content_hash,
            'children': [c.to_dict() for c in self.children],
        }


def build_tree(classified_lines):
    """classified_lines: list of (kind, number, text) tuples in document order.
    Nesting comes from the NUMBER STRING itself (e.g. 2.1.1.1's parent is
    whichever open ancestor's number is '2.1'), not from font size —
    this is what correctly handles the depth-skip irregularity."""
    root_nodes = []
    stack = []  # list of Node objects, ancestors currently open

    def is_ancestor(candidate_parts, node_parts):
        return len(candidate_parts) < len(node_parts) and \
            node_parts[:len(candidate_parts)] == candidate_parts

    for kind, number, text in classified_lines:
        if kind == 'heading':
            parts = number.split('.')
            while stack and not is_ancestor(stack[-1].number.split('.'), parts):
                stack.pop()
            parent = stack[-1] if stack else None
            node = Node(number, text, level=len(parts), parent=parent)
            if parent:
                parent.children.append(node)
            else:
                root_nodes.append(node)
            stack.append(node)
        else:
            if stack:
                stack[-1].body_lines.append(text)

    def sort_key(n):
        return [int(p) for p in n.number.split('.')]

    def sort_recursively(nodes):
        nodes.sort(key=sort_key)
        for n in nodes:
            sort_recursively(n.children)
        return nodes

    return sort_recursively(root_nodes)


def flatten(nodes):
    out = []
    for n in nodes:
        out.append(n)
        out.extend(flatten(n.children))
    return out