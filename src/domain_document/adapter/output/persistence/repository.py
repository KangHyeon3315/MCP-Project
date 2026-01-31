from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql.expression import over # Correct import for over()
from typing import Optional, List
import uuid
from datetime import datetime, timezone # Import datetime and timezone

from src.domain_document.application.port.output.document_repository_port import DocumentRepositoryPort
from src.domain_document.domain.model.document import DomainDocument, DomainProperty, DomainPolicy
from src.domain_document.adapter.output.persistence.entity import (
    DomainDocumentEntity, DomainPropertyEntity, DomainPolicyEntity
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
        """
        Saves a new version of a domain document. This is always an insert.
        """
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
                display_order=idx,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            entity.properties.append(prop_entity)

        for policy in document.policies:
            policy_entity = DomainPolicyEntity(
                identifier=uuid.uuid4(),
                domain_identifier=entity.identifier,
                category=policy.category,
                subject=policy.subject,
                content=policy.content,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
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

    def find_latest_by_logical_key(self, project: str, service: str, domain: str) -> Optional[DomainDocument]:
        entity = self._session.query(DomainDocumentEntity).filter_by(
            project=project,
            service=service,
            domain=domain
        ).order_by(DomainDocumentEntity.version.desc()).first()
        return to_domain(entity) if entity else None

    def find_all_versions_by_logical_key(self, project: str, service: str, domain: str) -> List[DomainDocument]:
        entities = self._session.query(DomainDocumentEntity).filter_by(
            project=project,
            service=service,
            domain=domain
        ).order_by(DomainDocumentEntity.version.desc()).all()
        return [to_domain(entity) for entity in entities]

    def find_all_latest_by_project(self, project: str) -> List[DomainDocument]:
        """
        Uses PostgreSQL's DISTINCT ON to efficiently find the latest version of each document.
        """
        latest_versions = self._session.query(DomainDocumentEntity).distinct(
            DomainDocumentEntity.project,
            DomainDocumentEntity.service,
            DomainDocumentEntity.domain
        ).filter(
            DomainDocumentEntity.project == project
        ).order_by(
            DomainDocumentEntity.project,
            DomainDocumentEntity.service,
            DomainDocumentEntity.domain,
            DomainDocumentEntity.version.desc()
        ).all()

        return [to_domain(entity) for entity in latest_versions]

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names from domain documents.
        """
        project_tuples = self._session.query(DomainDocumentEntity.project).distinct().all()
        return [project[0] for project in project_tuples]

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
