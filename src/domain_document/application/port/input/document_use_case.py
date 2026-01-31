from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from datetime import datetime

from src.domain_document.domain.model.document import DomainDocument


class DocumentUseCase(ABC):
    """
    Input port defining the use cases for managing domain documents.
    The application service will implement this interface.
    """

    @abstractmethod
    def create_document(self, project: str, service: str, domain: str, summary: str, properties: list, policies: list, created_at: datetime, updated_at: datetime) -> DomainDocument:
        """
        Use case for creating a new domain document.
        """
        raise NotImplementedError

    @abstractmethod
    def get_document_by_full_name(self, project: str, service: str, domain: str, version: int) -> Optional[DomainDocument]:
        """
        Use case for retrieving a specific version of a domain document.
        """
        raise NotImplementedError

    @abstractmethod
    def get_document_context(self, identifier: uuid.UUID) -> Optional[dict]:
        """
        Use case for retrieving the full context of a domain document.
        """
        raise NotImplementedError
