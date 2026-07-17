from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Selection, SelectionNode, DBNode
from app.schemas import SelectionIn

router = APIRouter(prefix="/selections", tags=["selections"])


@router.post("")
def create_selection(payload: SelectionIn, db: Session = Depends(get_db)):
    sel = Selection(name=payload.name)
    db.add(sel)
    db.commit()
    for node_id in payload.node_ids:
        node = db.query(DBNode).get(node_id)
        if not node:
            raise HTTPException(404, f"Node {node_id} not found")
        db.add(SelectionNode(selection_id=sel.id, node_id=node.id, version=node.version))
    db.commit()
    return {"selection_id": sel.id, "name": sel.name, "node_ids": payload.node_ids}