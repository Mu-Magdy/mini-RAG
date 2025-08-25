from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship

class Asset(SQLAlchemyBase):
  __tablename__ = "assets"
  asset_id = Column(Integer, primary_key=True,autoincrement=True)
  asset_uuid=Column(UUID(as_uuid=True), nullable=False,default=uuid.uuid4,unique=True)

  asset_type = Column(String, nullable=False)
  asset_name = Column(String, nullable=False)
  asset_size = Column(Integer, nullable=True)
  asset_config = Column(JSONB, nullable=True)

  asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)


  project = relationship("Project", back_populates="assets")
  chunks = relationship("DataChunk", back_populates="asset")
  __table_args__ = (
    Index("ix_asset_project_id",asset_project_id),
    Index("ix_asset_type",asset_type),
  )
  
  created_at = Column(DateTime(timezone=True), nullable=False,server_default=func.now())
  updated_at = Column(DateTime(timezone=True), nullable=True,onupdate=func.now())

