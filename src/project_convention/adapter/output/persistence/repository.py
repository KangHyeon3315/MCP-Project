from sqlalchemy.orm import Session
from sqlalchemy import func, text
from sqlalchemy.sql.expression import over # Correct import for over()
from typing import Optional, List, Tuple
import uuid
from datetime import datetime, timezone

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
        if entity and entity.deleted_at is None:
            return to_domain(entity)
        return None

    def find_by_project(self, project: str) -> List[ProjectConvention]:
        entities = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.deleted_at.is_(None)
        ).all()
        return [to_domain(entity) for entity in entities]

    def find_by_project_and_category(self, project: str, category: str) -> List[ProjectConvention]:
        entities = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.category == category,
            ProjectConventionEntity.deleted_at.is_(None)
        ).all()
        return [to_domain(entity) for entity in entities]

    def find_latest_by_project_and_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Uses PostgreSQL's DISTINCT ON to efficiently find the latest version of each convention
        for a given project and category.
        """
        # Subquery to find latest versions.
        latest_identifiers_query = self._session.query(ProjectConventionEntity.identifier)\
            .distinct(
                ProjectConventionEntity.project,
                ProjectConventionEntity.category,
                ProjectConventionEntity.title
            ).filter(
                ProjectConventionEntity.project == project,
                ProjectConventionEntity.category == category,
                ProjectConventionEntity.deleted_at.is_(None)
            ).order_by(
                ProjectConventionEntity.project,
                ProjectConventionEntity.category,
                ProjectConventionEntity.title,
                ProjectConventionEntity.version.desc()
            ).subquery()
        
        entities = self._session.query(ProjectConventionEntity)\
            .filter(ProjectConventionEntity.identifier.in_(latest_identifiers_query))\
            .order_by(
                ProjectConventionEntity.project,
                ProjectConventionEntity.category,
                ProjectConventionEntity.title,
                ProjectConventionEntity.version.desc()
            ).all()

        return [to_domain(entity) for entity in entities]

    def find_latest_by_logical_key(self, project: str, category: str, title: str) -> Optional[ProjectConvention]:
        """
        Finds the latest version of a single convention by its logical key.
        """
        entity = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.category == category,
            ProjectConventionEntity.title == title,
            ProjectConventionEntity.deleted_at.is_(None)
        ).order_by(ProjectConventionEntity.version.desc()).first()
        
        return to_domain(entity) if entity else None

    def find_all_versions_by_logical_key(self, project: str, category: str, title: str) -> List[ProjectConvention]:
        """
        Finds all versions of a single convention by its logical key, ordered by version descending.
        """
        entities = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.category == category,
            ProjectConventionEntity.title == title,
            ProjectConventionEntity.deleted_at.is_(None)
        ).order_by(ProjectConventionEntity.version.desc()).all()
        return [to_domain(entity) for entity in entities]

    def find_all_latest_by_project(self, project: str) -> List[ProjectConvention]:
        """
        Uses PostgreSQL's DISTINCT ON to efficiently find the latest version of each convention.
        """
        # We need to filter out deleted items before applying DISTINCT ON
        subquery = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.deleted_at.is_(None)
        ).subquery()

        latest_versions = self._session.query(subquery).distinct(
            subquery.c.project,
            subquery.c.category,
            subquery.c.title
        ).order_by(
            subquery.c.project,
            subquery.c.category,
            subquery.c.title,
            subquery.c.version.desc()
        ).all()
        
        # The result of a subquery query is a KeyedTuple, not the entity directly
        # A simple to_domain mapping won't work. We need to create the domain model from the tuple.
        return [ProjectConvention.model_validate(row, from_attributes=True) for row in latest_versions]

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names from project conventions.
        """
        project_tuples = self._session.query(ProjectConventionEntity.project).filter(
            ProjectConventionEntity.deleted_at.is_(None)
        ).distinct().all()
        return [project[0] for project in project_tuples]

    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        # Hard delete (only use if necessary, prefer soft-delete)
        entity = self._session.get(ProjectConventionEntity, identifier)
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False

    def soft_delete_all_versions_by_logical_key(self, project: str, category: str, title: str) -> int:
        """
        Soft-deletes all versions of a project convention by setting the deleted_at timestamp.
        """
        now = datetime.now(timezone.utc)
        result = self._session.query(ProjectConventionEntity).filter(
            ProjectConventionEntity.project == project,
            ProjectConventionEntity.category == category,
            ProjectConventionEntity.title == title,
            ProjectConventionEntity.deleted_at.is_(None) # Only soft-delete non-deleted items
        ).update(
            {ProjectConventionEntity.deleted_at: now},
            synchronize_session=False
        )
        self._session.commit()
        return result

    def update_embedding(self, convention_id: str, embedding: List[float]) -> None:
        """
        컨벤션의 임베딩 업데이트

        Args:
            convention_id: 컨벤션 식별자
            embedding: 임베딩 벡터 (384차원)
        """
        # Convert list to string format for pgvector
        embedding_str = f"[{','.join(map(str, embedding))}]"

        self._session.execute(
            text("""
                UPDATE project_convention
                SET embedding = CAST(:embedding_str AS vector),
                    updated_at = NOW()
                WHERE identifier = :convention_id
            """),
            {"convention_id": convention_id, "embedding_str": embedding_str}
        )
        self._session.commit()

    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> List[Tuple[ProjectConvention, float]]:
        """
        벡터 유사도 검색

        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 최대 반환 결과 수
            similarity_threshold: 최소 유사도 임계값 (0.0 ~ 1.0)

        Returns:
            (ProjectConvention, similarity) 튜플 리스트
        """
        # Convert list to string format for pgvector
        query_vector_str = f"[{','.join(map(str, query_embedding))}]"

        # SQL 쿼리로 벡터 검색 수행
        query = text("""
            SELECT identifier,
                   1 - (embedding <=> CAST(:query_vector_str AS vector)) as similarity
            FROM project_convention
            WHERE deleted_at IS NULL
              AND embedding IS NOT NULL
              AND 1 - (embedding <=> CAST(:query_vector_str AS vector)) > :threshold
            ORDER BY embedding <=> CAST(:query_vector_str AS vector)
            LIMIT :top_k
        """)

        result = self._session.execute(
            query,
            {
                "query_vector_str": query_vector_str,
                "threshold": similarity_threshold,
                "top_k": top_k
            }
        )

        # 결과를 ProjectConvention 객체로 변환
        results = []
        for row in result:
            convention_id = row.identifier
            similarity = row.similarity

            # 컨벤션 조회
            entity = self._session.get(ProjectConventionEntity, convention_id)

            if entity:
                convention = to_domain(entity)
                results.append((convention, similarity))

        return results
