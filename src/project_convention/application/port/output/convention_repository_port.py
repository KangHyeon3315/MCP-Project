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
    def delete_by_identifier(self, identifier: uuid.UUID) -> bool:
        """
        Deletes a project convention by its unique identifier. Returns True on success.
        """
        raise NotImplementedError
