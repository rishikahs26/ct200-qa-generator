1. Data model — the 5 tables and why (Document/DBNode/Selection/
SelectionNode/Generation).
2. Parsing decisions — list each irregularity found (hyphen-glyph
splitting, table double-detection, 2.1.1.1 depth-skip sharing a font
size with table headers, out-of-order headings 3.1→3.2→3.4→3.3, table
cells wrapping across lines) and exactly how your code handles each one.
3. Versioning strategy — stable_key = section number; justify it;
state the known failure mode (renumbered sections look like remove+add).
4. LLM prompt design + retry strategy — the prompt, the one-retry
policy, and why you fail loudly (LLMGenerationError → HTTP 502) instead
of silently storing bad data.
5. What you'd do differently with more time — e.g. severity-aware
staleness (numeric diff, not just hash equality), fuzzy title matching as
a fallback when stable_key matching fails.
6. Decision log:
    a.What's the one part of this system most likely to silently give wrong results without erroring? How would you catch it? 
    -> The PDF parser/tree-builder is the most likely part to produce silent errors because incorrect heading detection can create a wrong document hierarchy.
    I would catch this by adding post-parsing validation for heading relationships, numbering consistency, and missing sections.If the structure is uncertain, the system should raise a warning instead of continuing with incorrect data.

    b.Where did you choose simplicity over correctness because of time, and what would 
    break first if this went to production as-is?
    -> I chose simplicity in versioning by using the section number as the stable_key and hash comparison for detecting changes.This works well for normal updates but fails when sections are renamed, moved, or renumbered.In that case, the system may incorrectly treat an edited section as a deleted section and a new section.A better approach would combine section numbers with title and content similarity matching

    c.Name one input (to your parser, your versioning matcher, or your LLM call) that you did 
    not handle, and what your system does when it sees it.
    -> One input not handled currently is a heading with an unusual format like "3.1A" or "Section 3.1".The parser expects standard numeric section formats, so these headings may be treated as normal text.The system continues running but the section may be missing from the document tree.This can affect test generation and version comparison for that section
