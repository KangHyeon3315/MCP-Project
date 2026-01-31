from typing import Optional, List
import uuid
from datetime import datetime, timezone

from src.project_convention.domain.model.convention import ProjectConvention
from src.project_convention.application.port.output.convention_repository_port import ConventionRepositoryPort
from src.project_convention.application.port.input.convention_use_case import ConventionUseCase


class ConventionService(ConventionUseCase):
    """
    Implementation of the ConventionUseCase.
    This service contains the core business logic for managing project conventions.
    """

    def __init__(self, convention_repository: ConventionRepositoryPort):
        self._repository = convention_repository

    def add_convention(self, project: str, category: str, title: str, content: str, example_correct: Optional[str], example_incorrect: Optional[str], created_at: datetime, updated_at: datetime) -> ProjectConvention:
        """
        Adds a new project convention.
        """
        new_convention = ProjectConvention(
            identifier=uuid.uuid4(),
            project=project,
            category=category,
            title=title,
            content=content,
            example_correct=example_correct,
            example_incorrect=example_incorrect,
            created_at=created_at,
            updated_at=updated_at
        )
        return self._repository.save(new_convention)

    def get_conventions_for_project(self, project: str) -> List[ProjectConvention]:
        """
        Retrieves all conventions for a specific project.
        """
        return self._repository.find_by_project(project)

    def get_conventions_by_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Retrieves all conventions for a specific project and category.
        """
        return self._repository.find_by_project_and_category(project, category)
