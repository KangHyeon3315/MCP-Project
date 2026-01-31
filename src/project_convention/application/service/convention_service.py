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

    def create_or_update_convention(self, project: str, category: str, title: str, content: str, example_correct: Optional[str], example_incorrect: Optional[str]) -> ProjectConvention:
        """
        Creates a new convention or a new version of an existing one.
        """
        latest_version = self._repository.find_latest_by_logical_key(
            project=project,
            category=category,
            title=title
        )
        
        new_version_number = 1
        if latest_version:
            new_version_number = latest_version.version + 1

        new_convention = ProjectConvention(
            identifier=uuid.uuid4(),
            project=project,
            category=category,
            title=title,
            version=new_version_number,
            content=content,
            example_correct=example_correct,
            example_incorrect=example_incorrect,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        return self._repository.save(new_convention)

    def get_latest_conventions_for_project(self, project: str) -> List[ProjectConvention]:
        """
        Retrieves the latest version of all conventions for a specific project.
        """
        return self._repository.find_all_latest_by_project(project)

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        return self._repository.get_all_unique_project_names()

    def get_all_versions_of_convention(self, project: str, category: str, title: str) -> List[ProjectConvention]:
        """
        Retrieves all versions of a single convention.
        """
        return self._repository.find_all_versions_by_logical_key(project, category, title)

    def get_conventions_by_category(self, project: str, category: str) -> List[ProjectConvention]:
        """
        Retrieves all conventions for a specific project and category.
        NOTE: This still fetches all versions. For versioning, this should be updated.
        """
        return self._repository.find_by_project_and_category(project, category)
