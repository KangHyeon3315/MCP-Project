from typing import List
import logging

from ...application.port.output.embedding_port import EmbeddingPort
from ....domain_document.domain.model.document import DomainDocument
from ....project_convention.domain.model.convention import ProjectConvention

logger = logging.getLogger(__name__)


class EmbeddingService:
    """임베딩 생성 및 관리 서비스"""

    def __init__(
        self,
        embedding_adapter: EmbeddingPort,
        domain_repository,
        convention_repository
    ):
        self._embedding_adapter = embedding_adapter
        self._domain_repo = domain_repository
        self._convention_repo = convention_repository

    def create_embedding_for_document(self, document: DomainDocument) -> None:
        """
        도메인 문서에 대한 임베딩 생성 및 저장

        Args:
            document: 도메인 문서
        """
        try:
            text = self._create_document_text(document)
            embedding = self._embedding_adapter.generate_embedding(text)
            self._domain_repo.update_embedding(str(document.identifier), embedding)
            logger.info(f"Created embedding for document: {document.identifier}")
        except Exception as e:
            logger.error(f"Failed to create embedding for document {document.identifier}: {e}")
            raise

    def create_embedding_for_convention(self, convention: ProjectConvention) -> None:
        """
        컨벤션에 대한 임베딩 생성 및 저장

        Args:
            convention: 프로젝트 컨벤션
        """
        try:
            text = self._create_convention_text(convention)
            embedding = self._embedding_adapter.generate_embedding(text)
            self._convention_repo.update_embedding(str(convention.identifier), embedding)
            logger.info(f"Created embedding for convention: {convention.identifier}")
        except Exception as e:
            logger.error(f"Failed to create embedding for convention {convention.identifier}: {e}")
            raise

    def _create_document_text(self, doc: DomainDocument) -> str:
        """
        도메인 문서를 검색 가능한 텍스트로 변환

        Args:
            doc: 도메인 문서

        Returns:
            검색용 텍스트
        """
        parts = [
            f"도메인: {doc.domain}",
            f"프로젝트: {doc.project}",
            f"서비스: {doc.service}",
            f"요약: {doc.summary}",
        ]

        if doc.properties:
            props = ", ".join([
                f"{p.name}({p.type}): {p.description}"
                for p in doc.properties
            ])
            parts.append(f"속성: {props}")

        if doc.policies:
            policies = ", ".join([
                f"{p.category} - {p.content}"
                for p in doc.policies
            ])
            parts.append(f"정책: {policies}")

        return " | ".join(parts)

    def _create_convention_text(self, conv: ProjectConvention) -> str:
        """
        컨벤션을 검색 가능한 텍스트로 변환

        Args:
            conv: 프로젝트 컨벤션

        Returns:
            검색용 텍스트
        """
        parts = [
            f"컨벤션: {conv.title}",
            f"분류: {conv.category}",
            f"내용: {conv.content}",
        ]

        if conv.example_correct:
            parts.append(f"올바른 예시: {conv.example_correct}")

        if conv.example_incorrect:
            parts.append(f"잘못된 예시: {conv.example_incorrect}")

        return " | ".join(parts)
