from typing import Dict, Any
import logging

from ...domain.model.search_result import SearchResult, DocumentMatch
from ...application.port.output.embedding_port import EmbeddingPort
from ....domain_document.domain.model.document import DomainDocument
from ....project_convention.domain.model.convention import ProjectConvention

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """시맨틱 검색 서비스"""

    def __init__(
        self,
        embedding_adapter: EmbeddingPort,
        domain_repository,
        convention_repository
    ):
        self._embedding_adapter = embedding_adapter
        self._domain_repo = domain_repository
        self._convention_repo = convention_repository

    def search(
        self,
        query: str,
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> SearchResult:
        """
        자연어 쿼리로 시맨틱 검색

        Args:
            query: 검색 쿼리
            top_k: 최대 반환 결과 수
            similarity_threshold: 최소 유사도 임계값 (0.0 ~ 1.0)

        Returns:
            검색 결과
        """
        logger.info(f"Semantic search query: '{query}' (top_k={top_k}, threshold={similarity_threshold})")

        # 1. 쿼리 임베딩 생성
        query_embedding = self._embedding_adapter.generate_embedding(query)

        # 2. 두 테이블 모두 검색
        domain_results = self._domain_repo.semantic_search(
            query_embedding, top_k, similarity_threshold
        )
        convention_results = self._convention_repo.semantic_search(
            query_embedding, top_k, similarity_threshold
        )

        # 3. 결과 병합 및 정렬
        matches = []

        for doc, similarity in domain_results:
            matches.append(DocumentMatch(
                document_type="DOMAIN_DOCUMENT",
                document_id=str(doc.identifier),
                similarity=similarity,
                content=self._document_to_dict(doc)
            ))

        for conv, similarity in convention_results:
            matches.append(DocumentMatch(
                document_type="PROJECT_CONVENTION",
                document_id=str(conv.identifier),
                similarity=similarity,
                content=self._convention_to_dict(conv)
            ))

        # 유사도 순으로 정렬 후 top_k개만 선택
        matches.sort(key=lambda x: x.similarity, reverse=True)
        matches = matches[:top_k]

        logger.info(f"Found {len(matches)} results")

        return SearchResult(
            query=query,
            matches=matches,
            total_count=len(matches)
        )

    def _document_to_dict(self, doc: DomainDocument) -> Dict[str, Any]:
        """도메인 문서를 딕셔너리로 변환"""
        return {
            "identifier": str(doc.identifier),
            "project": doc.project,
            "service": doc.service,
            "domain": doc.domain,
            "summary": doc.summary,
            "version": doc.version,
            "properties": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "is_required": p.is_required,
                    "is_immutable": p.is_immutable
                }
                for p in doc.properties
            ] if doc.properties else [],
            "policies": [
                {
                    "category": p.category,
                    "subject": p.subject,
                    "content": p.content
                }
                for p in doc.policies
            ] if doc.policies else []
        }

    def _convention_to_dict(self, conv: ProjectConvention) -> Dict[str, Any]:
        """컨벤션을 딕셔너리로 변환"""
        return {
            "identifier": str(conv.identifier),
            "project": conv.project,
            "category": conv.category,
            "title": conv.title,
            "content": conv.content,
            "example_correct": conv.example_correct,
            "example_incorrect": conv.example_incorrect,
            "version": conv.version
        }
