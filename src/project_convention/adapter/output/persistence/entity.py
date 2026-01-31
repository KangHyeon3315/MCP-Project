import uuid
from sqlalchemy import Column, String, TIMESTAMP, TEXT, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

Base = declarative_base()


class ProjectConventionEntity(Base):
    __tablename__ = 'project_convention'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    version = Column(Integer, nullable=False) # Add version column
    content = Column(TEXT, nullable=False) # VARCHAR can be limited, using TEXT for flexibility
    example_correct = Column(TEXT)
    example_incorrect = Column(TEXT)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('project', 'category', 'title', 'version', name='uq_project_convention'),)
