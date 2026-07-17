def match_and_diff(prev_nodes, curr_nodes):
    """Matches nodes across versions by stable_key (the section number, e.g. '2.1.1.1').
    Chosen because it's the only identifier guaranteed present and stable even
    when wording changes. Known failure mode: if a section is RENUMBERED
    (not just reworded), this reports it as remove+add instead of an edit."""
    prev_by_key = {n.stable_key: n for n in prev_nodes}
    curr_by_key = {n.stable_key: n for n in curr_nodes}

    changed, added = [], []
    for key, cn in curr_by_key.items():
        pn = prev_by_key.get(key)
        if pn is None:
            added.append({"stable_key": key, "heading": cn.heading})
        elif pn.content_hash != cn.content_hash:
            changed.append({
                "stable_key": key, "heading": cn.heading,
                "old_text_preview": pn.body_text[:120],
                "new_text_preview": cn.body_text[:120],
            })
    removed = [{"stable_key": k, "heading": prev_by_key[k].heading}
               for k in prev_by_key if k not in curr_by_key]

    return {"changed": changed, "added": added, "removed": removed}