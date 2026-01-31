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
    def add_convention(self, project: str, category: str, title: str, content: str, example_correct: Optional[str], example_incorrect: Optional[str], created_at: datetime, updated_at: datetime) -> ProjectConvention:
        """
        Use case for adding a new project convention.
        """
        raise NotImplementedError

    @abstractmethod
    def get_conventions_for_project(self, project: str) -> List[ProjectConvention]:
        """
        Use case for retrieving all conventions for a specific project.
        """
        raise NotImplementedError

    @abstractmethod
    def get_conventions_by_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Use case for retrieving all conventions for a specific project and category.
        """
        raise NotImplementedError
