import uuid
from sqlalchemy import (
    create_engine, Column, String, Integer, TIMESTAMP, BOOLEAN, ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class DomainDocumentEntity(Base):
    __tablename__ = 'domain_document'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project = Column(String, nullable=False)
    service = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    version = Column(Integer, nullable=False) # 버전 (애플리케이션에서 제어)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True) # For soft-delete
    embedding = Column(Vector(384), nullable=True) # Vector embedding for semantic search


    properties = relationship("DomainPropertyEntity", back_populates="domain_document", cascade="all, delete-orphan")
    policies = relationship("DomainPolicyEntity", back_populates="domain_document", cascade="all, delete-orphan")
    
    source_relationships = relationship(
        "DomainRelationshipEntity",
        foreign_keys="[DomainRelationshipEntity.source_domain_identifier]",
        back_populates="source_domain",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "DomainRelationshipEntity",
        foreign_keys="[DomainRelationshipEntity.target_domain_identifier]",
        back_populates="target_domain",
        cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint('project', 'service', 'domain', 'version', name='uq_domain_document'),)


class DomainPropertyEntity(Base):
    __tablename__ = 'domain_property'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_identifier = Column(UUID(as_uuid=True), ForeignKey('domain_document.identifier', ondelete="CASCADE"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    is_required = Column(BOOLEAN, nullable=False)
    is_immutable = Column(BOOLEAN, nullable=False)
    display_order = Column(Integer, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    domain_document = relationship("DomainDocumentEntity", back_populates="properties")
    enum_values = relationship("DomainEnumValueEntity", back_populates="property", cascade="all, delete-orphan")


class DomainEnumValueEntity(Base):
    __tablename__ = 'domain_enum_value'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_identifier = Column(UUID(as_uuid=True), ForeignKey('domain_property.identifier', ondelete="CASCADE"), nullable=False)
    
    enum_key = Column(String, nullable=False)
    enum_description = Column(String)

    property = relationship("DomainPropertyEntity", back_populates="enum_values")


class DomainPolicyEntity(Base):
    __tablename__ = 'domain_policy'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_identifier = Column(UUID(as_uuid=True), ForeignKey('domain_document.identifier', ondelete="CASCADE"), nullable=False)
    
    category = Column(String, nullable=False)
    subject = Column(String)
    content = Column(String, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    domain_document = relationship("DomainDocumentEntity", back_populates="policies")


class DomainRelationshipEntity(Base):
    __tablename__ = 'domain_relationship'

    identifier = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_domain_identifier = Column(UUID(as_uuid=True), ForeignKey('domain_document.identifier', ondelete="CASCADE"), nullable=False)
    target_domain_identifier = Column(UUID(as_uuid=True), ForeignKey('domain_document.identifier', ondelete="CASCADE"), nullable=False)
    
    relation_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    impact_description = Column(String)
    
    source_property_identifier = Column(UUID(as_uuid=True))
    target_property_identifier = Column(UUID(as_uuid=True))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    source_domain = relationship("DomainDocumentEntity", foreign_keys=[source_domain_identifier], back_populates="source_relationships")
    target_domain = relationship("DomainDocumentEntity", foreign_keys=[target_domain_identifier], back_populates="target_relationships")

