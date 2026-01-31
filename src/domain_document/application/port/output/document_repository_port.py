from abc import ABC, abstractmethod
from typing import Optional, List
import uuid

from src.domain_document.domain.model.document import DomainDocument


class DocumentRepositoryPort(ABC):
    """
    An output port for persisting and retrieving domain documents.
    """

    @abstractmethod
    def save(self, document: DomainDocument) -> DomainDocument:
        """
        Saves a domain document aggregate.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_identifier(self, identifier: uuid.UUID) -> Optional[DomainDocument]:
        """
        Finds a domain document by its unique identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_full_name(self, project: str, service: str, domain: str, version: int) -> Optional[DomainDocument]:
        """
        Finds a domain document by its full logical name and version.
        """
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_logical_key(self, project: str, service: str, domain: str) -> Optional[DomainDocument]:
        """
        Finds the latest version of a single domain document by its logical key.
        """
        raise NotImplementedError

    @abstractmethod
    def find_all_versions_by_logical_key(self, project: str, service: str, domain: str) -> List[DomainDocument]:
        """
        Finds all versions of a single domain document by its logical key.
        """
        raise NotImplementedError

    @abstractmethod
    def find_all_latest_by_project(self, project: str) -> List[DomainDocument]:
        """
        Finds only the latest version of each domain document for a given project.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        raise NotImplementedError

    @abstractmethod
    def find_all_by_project(self, project: str) -> List[DomainDocument]:
        """
        Finds all domain documents for a given project.
        """
        raise NotImplementedError
        
    @abstractmethod
    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        """
        Deletes a domain document by its unique identifier. Returns True on success.
        """
        raise NotImplementedError

