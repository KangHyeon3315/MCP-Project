from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.project_convention.domain.model.convention import ProjectConvention


class ConventionUseCase(ABC):
    """
    Input port defining the use cases for managing project conventions.
    The application service will implement this interface.
    """

    @abstractmethod
    def create_or_update_convention(self, project: str, category: str, title: str, content: str, example_correct: Optional[str], example_incorrect: Optional[str]) -> ProjectConvention:
        """
        Use case for creating a new convention or updating an existing one by creating a new version.
        """
        raise NotImplementedError

    @abstractmethod
    def get_latest_conventions_for_project(self, project: str) -> List[ProjectConvention]:
        """
        Use case for retrieving the latest version of all conventions for a specific project.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_versions_of_convention(self, project: str, category: str, title: str) -> List[ProjectConvention]:
        """
        Use case for retrieving all versions of a single convention.
        """
        raise NotImplementedError

    @abstractmethod
    def get_conventions_by_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Use case for retrieving all conventions for a specific project and category.
        """
        raise NotImplementedError
