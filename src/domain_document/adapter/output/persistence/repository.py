from sqlalchemy.orm import Session, joinedload # Import joinedload
from sqlalchemy import func
from sqlalchemy.sql.expression import over # Correct import for over()
from typing import Optional, List
import uuid
from datetime import datetime, timezone # Import datetime and timezone

from src.domain_document.application.port.output.document_repository_port import DocumentRepositoryPort
from src.domain_document.domain.model.document import DomainDocument, DomainProperty, DomainPolicy, DomainRelationship # Import DomainRelationship
from src.domain_document.adapter.output.persistence.entity import (
    DomainDocumentEntity, DomainPropertyEntity, DomainPolicyEntity, DomainRelationshipEntity # Import DomainRelationshipEntity
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

    # Implement full dependency mapping
    dependencies = []
    if entity.source_relationships:
        for rel_entity in entity.source_relationships:
            # Ensure target_domain is loaded for full name construction
            # Check if target_domain relationship is loaded and not None
            if rel_entity.target_domain:
                target_full_name = f"{rel_entity.target_domain.project}:{rel_entity.target_domain.service}:{rel_entity.target_domain.domain}"
                dependencies.append(
                    DomainRelationship(
                        target_domain=target_full_name,
                        relation_type=rel_entity.relation_type,
                        description=rel_entity.description,
                        impact_description=rel_entity.impact_description
                    )
                )

    return DomainDocument(
        identifier=entity.identifier,
        project=entity.project,
        service=entity.service,
        domain=entity.domain,
        summary=entity.summary,
        version=entity.version,
        properties=properties,
        policies=policies,
        dependencies=dependencies, # Now includes mapped dependencies
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
        # Eager load relationships for complete dependency mapping
        entity = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(
                DomainDocumentEntity.identifier == identifier,
                DomainDocumentEntity.deleted_at.is_(None)
            ).first()
        return to_domain(entity) if entity else None

    def find_by_full_name(self, project: str, service: str, domain: str, version: int) -> Optional[DomainDocument]:
        # Eager load relationships
        entity = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(
                DomainDocumentEntity.project == project,
                DomainDocumentEntity.service == service,
                DomainDocumentEntity.domain == domain,
                DomainDocumentEntity.version == version,
                DomainDocumentEntity.deleted_at.is_(None)
            ).first()
        return to_domain(entity) if entity else None

    def find_latest_by_logical_key(self, project: str, service: str, domain: str) -> Optional[DomainDocument]:
        # Eager load relationships
        entity = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(
                DomainDocumentEntity.project == project,
                DomainDocumentEntity.service == service,
                DomainDocumentEntity.domain == domain,
                DomainDocumentEntity.deleted_at.is_(None)
            ).order_by(DomainDocumentEntity.version.desc()).first()
        return to_domain(entity) if entity else None

    def find_all_versions_by_logical_key(self, project: str, service: str, domain: str) -> List[DomainDocument]:
        # Eager load relationships
        entities = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(
                DomainDocumentEntity.project == project,
                DomainDocumentEntity.service == service,
                DomainDocumentEntity.domain == domain,
                DomainDocumentEntity.deleted_at.is_(None)
            ).order_by(DomainDocumentEntity.version.desc()).all()
        return [to_domain(entity) for entity in entities]

    def find_all_latest_by_project(self, project: str) -> List[DomainDocument]:
        """
        Uses PostgreSQL's DISTINCT ON to efficiently find the latest version of each document.
        """
        # Subquery to find latest versions. Need to ensure eager loading works here.
        # This is more complex with joinedload on a subquery.
        # A simpler approach for find_all_latest_by_project might be to fetch
        # the main entities and then separately load their relationships if needed.
        # However, for consistency and performance, eager loading is preferred.

        # One way to handle eager loading with DISTINCT ON is to select distinct
        # identifiers first, then query for those identifiers with eager loading.
        
        latest_identifiers_query = self._session.query(DomainDocumentEntity.identifier)\
            .distinct(
                DomainDocumentEntity.project,
                DomainDocumentEntity.service,
                DomainDocumentEntity.domain
            ).filter(
                DomainDocumentEntity.project == project,
                DomainDocumentEntity.deleted_at.is_(None)
            ).order_by(
                DomainDocumentEntity.project,
                DomainDocumentEntity.service,
                DomainDocumentEntity.domain,
                DomainDocumentEntity.version.desc()
            ).subquery()
        
        entities = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(DomainDocumentEntity.identifier.in_(latest_identifiers_query))\
            .order_by(
                DomainDocumentEntity.project, # Preserve original order from subquery
                DomainDocumentEntity.service,
                DomainDocumentEntity.domain,
                DomainDocumentEntity.version.desc()
            ).all()

        return [to_domain(entity) for entity in entities]

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names from domain documents.
        """
        project_tuples = self._session.query(DomainDocumentEntity.project).filter(
            DomainDocumentEntity.deleted_at.is_(None)
        ).distinct().all()
        return [project[0] for project in project_tuples]

    def find_all_by_project(self, project: str) -> List[DomainDocument]:
        # Eager load relationships
        entities = self._session.query(DomainDocumentEntity)\
            .options(
                joinedload(DomainDocumentEntity.properties),
                joinedload(DomainDocumentEntity.policies),
                joinedload(DomainDocumentEntity.source_relationships).joinedload(DomainRelationshipEntity.target_domain)
            )\
            .filter(
                DomainDocumentEntity.project == project,
                DomainDocumentEntity.deleted_at.is_(None)
            ).all()
        return [to_domain(entity) for entity in entities]

    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        # Hard delete (only use if necessary, prefer soft-delete)
        entity = self._session.query(DomainDocumentEntity).filter_by(identifier=identifier).first()
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False

    def soft_delete_all_versions_by_logical_key(self, project: str, service: str, domain: str) -> int:
        """
        Soft-deletes all versions of a domain document by setting the deleted_at timestamp.
        """
        now = datetime.now(timezone.utc)
        result = self._session.query(DomainDocumentEntity).filter(
            DomainDocumentEntity.project == project,
            DomainDocumentEntity.service == service,
            DomainDocumentEntity.domain == domain,
            DomainDocumentEntity.deleted_at.is_(None) # Only soft-delete non-deleted items
        ).update(
            {DomainDocumentEntity.deleted_at: now},
            synchronize_session=False
        )
        self._session.commit()
        return result
