from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Selection, SelectionNode, DBNode, Generation
from app.services.llm import generate_test_cases, LLMGenerationError
from app.services.staleness import check_stale

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post("/from-selection/{selection_id}")
def create_generation(selection_id: int, db: Session = Depends(get_db)):
    sel = db.query(Selection).get(selection_id)
    if not sel:
        raise HTTPException(404, "Selection not found")

    sel_nodes = db.query(SelectionNode).filter(SelectionNode.selection_id == selection_id).all()
    nodes = [db.query(DBNode).get(sn.node_id) for sn in sel_nodes]

    combined_text = "\n\n".join(f"{n.heading}\n{n.body_text}" for n in nodes)
    try:
        test_cases = generate_test_cases(combined_text)
    except LLMGenerationError as e:
        raise HTTPException(502, str(e))

    source_nodes = [{"stable_key": n.stable_key, "content_hash": n.content_hash, "version": n.version} for n in nodes]
    gen = Generation(
        selection_id=selection_id,
        source_nodes=source_nodes,
        llm_output=[tc.dict() for tc in test_cases],
    )
    db.add(gen)
    db.commit()
    return {"generation_id": gen.id, "test_cases": gen.llm_output}


@router.get("/{generation_id}")
def get_generation(generation_id: int, db: Session = Depends(get_db)):
    gen = db.query(Generation).get(generation_id)
    if not gen:
        raise HTTPException(404, "Generation not found")

    document_id = None
    sel_nodes = db.query(SelectionNode).filter(SelectionNode.selection_id == gen.selection_id).all()
    if sel_nodes:
        first_node = db.query(DBNode).get(sel_nodes[0].node_id)
        document_id = first_node.document_id

    staleness = check_stale(db, document_id, gen.source_nodes)
    return {
        "generation_id": gen.id,
        "test_cases": gen.llm_output,
        "staleness": staleness,
    }