from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql.expression import over # Correct import for over()
from typing import Optional, List
import uuid

from src.project_convention.application.port.output.convention_repository_port import ConventionRepositoryPort
from src.project_convention.domain.model.convention import ProjectConvention
from src.project_convention.adapter.output.persistence.entity import ProjectConventionEntity

def to_domain(entity: ProjectConventionEntity) -> ProjectConvention:
    return ProjectConvention.model_validate(entity)

def to_entity(domain_model: ProjectConvention) -> ProjectConventionEntity:
    """Creates a new entity from a domain model for insertion."""
    return ProjectConventionEntity(
        identifier=domain_model.identifier,
        project=domain_model.project,
        category=domain_model.category,
        title=domain_model.title,
        version=domain_model.version,
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
        """
        Saves a new version of a project convention. This is always an insert.
        """
        entity = to_entity(convention)
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

    def find_latest_by_logical_key(self, project: str, category: str, title: str) -> Optional[ProjectConvention]:
        """
        Finds the latest version of a single convention by its logical key.
        """
        entity = self._session.query(ProjectConventionEntity).filter_by(
            project=project,
            category=category,
            title=title
        ).order_by(ProjectConventionEntity.version.desc()).first()
        
        return to_domain(entity) if entity else None

    def find_all_versions_by_logical_key(self, project: str, category: str, title: str) -> List[ProjectConvention]:
        """
        Finds all versions of a single convention by its logical key, ordered by version descending.
        """
        entities = self._session.query(ProjectConventionEntity).filter_by(
            project=project,
            category=category,
            title=title
        ).order_by(ProjectConventionEntity.version.desc()).all()
        return [to_domain(entity) for entity in entities]

    def find_all_latest_by_project(self, project: str) -> List[ProjectConvention]:
        """
        Uses PostgreSQL's DISTINCT ON to efficiently find the latest version of each convention.
        """
        latest_versions = self._session.query(ProjectConventionEntity).distinct(
            ProjectConventionEntity.project,
            ProjectConventionEntity.category,
            ProjectConventionEntity.title
        ).filter(
            ProjectConventionEntity.project == project
        ).order_by(
            ProjectConventionEntity.project,
            ProjectConventionEntity.category,
            ProjectConventionEntity.title,
            ProjectConventionEntity.version.desc()
        ).all()
        
        return [to_domain(entity) for entity in latest_versions]

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names from project conventions.
        """
        project_tuples = self._session.query(ProjectConventionEntity.project).distinct().all()
        return [project[0] for project in project_tuples]

    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        entity = self._session.get(ProjectConventionEntity, identifier)
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False
