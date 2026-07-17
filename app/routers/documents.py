from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
import shutil, os, tempfile

from app.database import get_db
from app.models import Document, DBNode
from app.pdf_parser.lines import extract_lines, classify_line
from app.pdf_parser.tree_builder import build_tree, flatten
from app.services.versioning import match_and_diff

router = APIRouter(prefix="/documents", tags=["documents"])


def _ingest_pdf_to_nodes(db: Session, document_id: int, pdf_path: str, version: int):
    lines = extract_lines(pdf_path)
    classified = [classify_line(l) for l in lines]
    tree = build_tree(classified)

    id_map = {}
    for node in flatten(tree):
        parent_db_id = id_map[node.parent].id if node.parent else None
        db_node = DBNode(
            document_id=document_id, version=version,
            stable_key=node.stable_key, heading=node.heading,
            level=node.level, body_text=node.body_text,
            content_hash=node.content_hash, parent_id=parent_db_id,
        )
        db.add(db_node)
        db.flush()
        id_map[node] = db_node

    db.commit()
    return list(id_map.values())


@router.post("/{document_id}/ingest")
def ingest(document_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc = db.query(Document).get(document_id)
    if not doc:
        doc = Document(id=document_id, name=f"document-{document_id}")
        db.add(doc)
        db.commit()

    latest = db.query(func.max(DBNode.version)).filter(DBNode.document_id == document_id).scalar()
    version = (latest or 0) + 1

    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"upload_{document_id}_{version}.pdf")
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    nodes = _ingest_pdf_to_nodes(db, document_id, tmp_path, version)
    os.remove(tmp_path)
    return {"document_id": document_id, "version": version, "node_count": len(nodes)}


@router.get("/{document_id}/sections")
def top_level_sections(document_id: int, version: int = None, db: Session = Depends(get_db)):
    if version is None:
        version = db.query(func.max(DBNode.version)).filter(DBNode.document_id == document_id).scalar()
    nodes = db.query(DBNode).filter(
        DBNode.document_id == document_id, DBNode.version == version, DBNode.parent_id == None
    ).all()
    return [{"id": n.id, "heading": n.heading, "stable_key": n.stable_key} for n in nodes]


@router.get("/{document_id}/versions/{version}/diff")
def diff_versions(document_id: int, version: int, db: Session = Depends(get_db)):
    prev_nodes = db.query(DBNode).filter(DBNode.document_id == document_id, DBNode.version == version - 1).all()
    curr_nodes = db.query(DBNode).filter(DBNode.document_id == document_id, DBNode.version == version).all()
    if not prev_nodes:
        raise HTTPException(404, "No previous version to diff against")
    return match_and_diff(prev_nodes, curr_nodes)