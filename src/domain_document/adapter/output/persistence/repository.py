from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime, timezone # Import datetime and timezone

from src.domain_document.application.port.output.document_repository_port import DocumentRepositoryPort
from src.domain_document.domain.model.document import DomainDocument, DomainProperty, DomainPolicy, DomainRelationship
from src.domain_document.adapter.output.persistence.entity import (
    DomainDocumentEntity, DomainPropertyEntity, DomainPolicyEntity, DomainEnumValueEntity, DomainRelationshipEntity
)

# This is a simplified mapper. In a real application, you might use a library like `automapper`.
def to_domain(entity: DomainDocumentEntity) -> DomainDocument:
    # This mapping needs to be comprehensive, including nested objects
    properties = [
        DomainProperty.model_validate(p_entity)
        for p_entity in entity.properties
    ] if entity.properties else []

    policies = [
        DomainPolicy.model_validate(pol_entity)
        for pol_entity in entity.policies
    ] if entity.policies else []

    # Simplified dependencies/used_by for now. Full mapping requires more complex logic
    # that might involve querying view_domain_full_context or doing more joins.
    dependencies = [] # TODO: implement full dependency mapping
    
    return DomainDocument(
        identifier=entity.identifier,
        project=entity.project,
        service=entity.service,
        domain=entity.domain,
        summary=entity.summary,
        version=entity.version,
        properties=properties,
        policies=policies,
        dependencies=dependencies,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

def to_entity(domain_model: DomainDocument) -> DomainDocumentEntity:
    # This function creates a new entity from a domain model.
    # It does NOT handle updates or existing nested objects.
    return DomainDocumentEntity(
        identifier=domain_model.identifier,
        project=domain_model.project,
        service=domain_model.service,
        domain=domain_model.domain,
        summary=domain_model.summary,
        version=domain_model.version,
        created_at=domain_model.created_at,
        updated_at=domain_model.updated_at
    )


class DocumentRepository(DocumentRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def save(self, document: DomainDocument) -> DomainDocument:
        entity = self._session.get(DomainDocumentEntity, document.identifier)
        if entity:
            # Update existing entity
            entity.project = document.project
            entity.service = document.service
            entity.domain = document.domain
            entity.summary = document.summary
            entity.version = document.version
            # Created_at should not be updated. Updated_at handled by DB.

            # Handle nested properties and policies
            # This is a simplified approach, a more robust solution would involve
            # comparing existing properties/policies and updating/deleting/adding as needed.
            # For this example, we'll clear and re-add.
            # Clear existing children
            entity.properties.clear()
            entity.policies.clear()

            for idx, prop in enumerate(document.properties):
                prop_entity = DomainPropertyEntity(
                    identifier=uuid.uuid4(), # New identifier for sub-entity
                    domain_identifier=entity.identifier,
                    name=prop.name,
                    description=prop.description,
                    type=prop.type,
                    is_required=prop.is_required,
                    is_immutable=prop.is_immutable,
                    display_order=idx, # Explicitly set display_order
                    created_at=datetime.now(timezone.utc), # Explicitly set
                    updated_at=datetime.now(timezone.utc)  # Explicitly set
                )
                # handle enum values if they exist in prop
                entity.properties.append(prop_entity)

            for policy in document.policies:
                policy_entity = DomainPolicyEntity(
                    identifier=uuid.uuid4(), # New identifier for sub-entity
                    domain_identifier=entity.identifier,
                    category=policy.category,
                    subject=policy.subject,
                    content=policy.content,
                    created_at=datetime.now(timezone.utc), # Explicitly set
                    updated_at=datetime.now(timezone.utc)  # Explicitly set
                )
                entity.policies.append(policy_entity)
            
        else:
            # Create new entity
            entity = to_entity(document)
            
            # Add nested properties and policies for a new document
            for idx, prop in enumerate(document.properties):
                prop_entity = DomainPropertyEntity(
                    identifier=uuid.uuid4(),
                    domain_identifier=entity.identifier,
                    name=prop.name,
                    description=prop.description,
                    type=prop.type,
                    is_required=prop.is_required,
                    is_immutable=prop.is_immutable,
                    display_order=idx, # Explicitly set display_order
                    created_at=datetime.now(timezone.utc), # Explicitly set
                    updated_at=datetime.now(timezone.utc)  # Explicitly set
                )
                entity.properties.append(prop_entity)

            for policy in document.policies:
                policy_entity = DomainPolicyEntity(
                    identifier=uuid.uuid4(),
                    domain_identifier=entity.identifier,
                    category=policy.category,
                    subject=policy.subject,
                    content=policy.content,
                    created_at=datetime.now(timezone.utc), # Explicitly set
                    updated_at=datetime.now(timezone.utc)  # Explicitly set
                )
                entity.policies.append(policy_entity)
            
            self._session.add(entity)
        
        self._session.commit()
        self._session.refresh(entity)
        return to_domain(entity)

    def find_by_identifier(self, identifier: uuid.UUID) -> Optional[DomainDocument]:
        entity = self._session.query(DomainDocumentEntity).filter_by(identifier=identifier).first()
        return to_domain(entity) if entity else None

    def find_by_full_name(self, project: str, service: str, domain: str, version: int) -> Optional[DomainDocument]:
        entity = self._session.query(DomainDocumentEntity).filter_by(
            project=project,
            service=service,
            domain=domain,
            version=version
        ).first()
        return to_domain(entity) if entity else None

    def find_all_by_project(self, project: str) -> List[DomainDocument]:
        entities = self._session.query(DomainDocumentEntity).filter_by(project=project).all()
        return [to_domain(entity) for entity in entities]

    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        entity = self._session.query(DomainDocumentEntity).filter_by(identifier=identifier).first()
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False
