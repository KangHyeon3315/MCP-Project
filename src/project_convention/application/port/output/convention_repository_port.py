from abc import ABC, abstractmethod
from typing import Optional, List
import uuid

from src.project_convention.domain.model.convention import ProjectConvention


class ConventionRepositoryPort(ABC):
    """
    An output port for persisting and retrieving project conventions.
    """

    @abstractmethod
    def save(self, convention: ProjectConvention) -> ProjectConvention:
        """
        Saves a project convention.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_identifier(self, identifier: uuid.UUID) -> Optional[ProjectConvention]:
        """
        Finds a project convention by its unique identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_project(self, project: str) -> List[ProjectConvention]:
        """
        Finds all conventions for a given project.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_project_and_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Finds all conventions for a given project and category.
        """
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_project_and_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Finds the latest version of each convention for a given project and category.
        """
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_logical_key(self, project: str, category: str, title: str) -> Optional[ProjectConvention]:
        """
        Finds the latest version of a single convention by its logical key.
        """
        raise NotImplementedError

    @abstractmethod
    def find_all_versions_by_logical_key(self, project: str, category: str, title: str) -> List[ProjectConvention]:
        """
        Finds all versions of a single convention by its logical key, ordered by version.
        """
        raise NotImplementedError

    @abstractmethod
    def find_all_latest_by_project(self, project: str) -> List[ProjectConvention]:
        """
        Finds only the latest version of each convention for a given project.
        """
        raise NotImplementedError
        
    @abstractmethod
    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        """
        Deletes a project convention by its unique identifier. Returns True on success.
        """
        raise NotImplementedError

    @abstractmethod
    def soft_delete_all_versions_by_logical_key(self, project: str, category: str, title: str) -> int:
        """
        Soft-deletes all versions of a project convention. Returns the number of affected rows.
        """
        raise NotImplementedError
