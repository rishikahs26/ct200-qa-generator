from sqlalchemy import func
from app.models import DBNode


def check_stale(db, document_id, source_nodes):
    """Compares the content_hash a Generation was created from against the
    CURRENT latest version's hash for that stable_key. Honest limitation:
    this can't distinguish a single reworded word from a changed clinical
    threshold -- both flip 'stale' identically."""
    if document_id is None:
        return {"stale": False, "stale_nodes": [], "note": "no source document found"}

    latest_version = db.query(func.max(DBNode.version)).filter(DBNode.document_id == document_id).scalar()
    stale_nodes = []
    for src in source_nodes:
        current = db.query(DBNode).filter(
            DBNode.document_id == document_id,
            DBNode.version == latest_version,
            DBNode.stable_key == src["stable_key"],
        ).first()
        if current is None:
            stale_nodes.append({"stable_key": src["stable_key"], "reason": "section removed"})
        elif current.content_hash != src["content_hash"]:
            stale_nodes.append({"stable_key": src["stable_key"], "reason": "content changed"})

    return {"stale": len(stale_nodes) > 0, "stale_nodes": stale_nodes}