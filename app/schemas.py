from pydantic import BaseModel
from typing import List, Optional


class NodeOut(BaseModel):
    id: int
    heading: str
    level: int
    body_text: str
    content_hash: str
    stable_key: str

    class Config:
        from_attributes = True


class SelectionIn(BaseModel):
    name: str
    node_ids: List[int]


class TestCase(BaseModel):
    title: str
    steps: List[str]
    expected_result: str