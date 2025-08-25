from pydantic import BaseModel
from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship

class DataChunk(SQLAlchemyBase):
  __tablename__ = "chunks"
  
  chunk_id = Column(Integer, primary_key=True,autoincrement=True)
  chunk_uuid=Column(UUID(as_uuid=True), nullable=False,default=uuid.uuid4,unique=True)
  
  chunk_text = Column(String, nullable=False)
  chunk_metadata = Column(JSONB, nullable=True)
  chunk_order = Column(Integer, nullable=False)
  
  chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
  chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

  project = relationship("Project", back_populates="chunks")
  asset = relationship("Asset", back_populates="chunks")
  
  
  created_at = Column(DateTime(timezone=True), nullable=False,server_default=func.now())
  updated_at = Column(DateTime(timezone=True), nullable=True,onupdate=func.now())
  
  __table_args__ = (
    Index("ix_chunk_project_id",chunk_project_id),
    Index("ix_chunk_asset_id",chunk_asset_id),
  )
  
  
class RetrievedDocument(BaseModel):
  text: str
  score: float