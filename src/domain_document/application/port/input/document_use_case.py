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
    def create_or_update_document(self, project: str, service: str, domain: str, summary: str, properties: list, policies: list) -> DomainDocument:
        """
        Use case for creating a new document or updating an existing one by creating a new version.
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

    @abstractmethod
    def find_all_latest_by_project(self, project: str) -> List[DomainDocument]:
        """
        Finds the latest version of all domain documents for a given project.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_versions_of_document(self, project: str, service: str, domain: str) -> List[DomainDocument]:
        """
        Use case for retrieving all versions of a single document.
        """
        raise NotImplementedError
