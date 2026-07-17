from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class DBNode(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version = Column(Integer, nullable=False)
    stable_key = Column(String, index=True)
    heading = Column(String)
    level = Column(Integer)
    body_text = Column(Text)
    content_hash = Column(String)
    parent_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)


class Selection(Base):
    __tablename__ = "selections"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class SelectionNode(Base):
    __tablename__ = "selection_nodes"
    id = Column(Integer, primary_key=True)
    selection_id = Column(Integer, ForeignKey("selections.id"))
    node_id = Column(Integer, ForeignKey("nodes.id"))
    version = Column(Integer)


class Generation(Base):
    __tablename__ = "generations"
    id = Column(Integer, primary_key=True)
    selection_id = Column(Integer, ForeignKey("selections.id"))
    source_nodes = Column(JSON)
    llm_output = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())