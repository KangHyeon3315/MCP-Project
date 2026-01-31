from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from src.project_convention.application.port.output.convention_repository_port import ConventionRepositoryPort
from src.project_convention.domain.model.convention import ProjectConvention
from src.project_convention.adapter.output.persistence.entity import ProjectConventionEntity

def to_domain(entity: ProjectConventionEntity) -> ProjectConvention:
    return ProjectConvention.model_validate(entity)

def to_entity(domain_model: ProjectConvention) -> ProjectConventionEntity:
    # This function creates a new entity from a domain model.
    # It does NOT handle updates or existing objects.
    return ProjectConventionEntity(
        identifier=domain_model.identifier,
        project=domain_model.project,
        category=domain_model.category,
        title=domain_model.title,
        content=domain_model.content,
        example_correct=domain_model.example_correct,
        example_incorrect=domain_model.example_incorrect,
        created_at=domain_model.created_at,
        updated_at=domain_model.updated_at
    )


class ConventionRepository(ConventionRepositoryPort):
    def __init__(self, session: Session):
        self._session = session

    def save(self, convention: ProjectConvention) -> ProjectConvention:
        entity = self._session.get(ProjectConventionEntity, convention.identifier)
        if entity: # Update
            entity.project = convention.project
            entity.category = convention.category
            entity.title = convention.title
            entity.content = convention.content
            entity.example_correct = convention.example_correct
            entity.example_incorrect = convention.example_incorrect
            # created_at should not be updated. updated_at is handled by DB.
        else: # Create
            entity = to_entity(convention) # Now to_entity will include created_at/updated_at
            self._session.add(entity)
            
        self._session.commit()
        self._session.refresh(entity)
        return to_domain(entity)

    def find_by_identifier(self, identifier: uuid.UUID) -> Optional[ProjectConvention]:
        entity = self._session.get(ProjectConventionEntity, identifier)
        return to_domain(entity) if entity else None

    def find_by_project(self, project: str) -> List[ProjectConvention]:
        entities = self._session.query(ProjectConventionEntity).filter_by(project=project).all()
        return [to_domain(entity) for entity in entities]

    def find_by_project_and_category(self, project: str, category: str) -> List[ProjectConvention]:
        entities = self._session.query(ProjectConventionEntity).filter_by(
            project=project,
            category=category
        ).all()
        return [to_domain(entity) for entity in entities]

    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        entity = self._session.get(ProjectConventionEntity, identifier)
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False
