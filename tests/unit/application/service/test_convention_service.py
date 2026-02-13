import pytest
from unittest.mock import Mock, MagicMock
import uuid
from datetime import datetime, timezone

from src.project_convention.application.service.convention_service import ConventionService
from src.project_convention.application.port.output.convention_repository_port import ConventionRepositoryPort
from src.project_convention.domain.model.convention import ProjectConvention

@pytest.fixture
def mock_convention_repository() -> Mock:
    return Mock(spec=ConventionRepositoryPort)

@pytest.fixture
def convention_service(mock_convention_repository: Mock) -> ConventionService:
    return ConventionService(convention_repository=mock_convention_repository)

@pytest.fixture
def sample_convention_data():
    return {
        "project": "TestProject",
        "category": "Naming",
        "title": "Variable Naming",
        "content": "Use snake_case for variables.",
        "example_correct": "user_name",
        "example_incorrect": "UserName"
    }

def test_create_new_convention(convention_service: ConventionService, mock_convention_repository: Mock, sample_convention_data):
    mock_convention_repository.find_latest_by_logical_key.return_value = None
    mock_convention_repository.save.side_effect = lambda conv: conv

    new_convention = convention_service.create_or_update_convention(**sample_convention_data)

    assert new_convention is not None
    assert isinstance(new_convention.identifier, uuid.UUID)
    assert new_convention.project == sample_convention_data["project"]
    assert new_convention.version == 1
    mock_convention_repository.save.assert_called_once()
    saved_conv = mock_convention_repository.save.call_args[0][0]
    assert saved_conv.version == 1

def test_create_new_version_of_convention(convention_service: ConventionService, mock_convention_repository: Mock, sample_convention_data):
    existing_conv = ProjectConvention(
        identifier=uuid.uuid4(),
        project=sample_convention_data["project"],
        category=sample_convention_data["category"],
        title=sample_convention_data["title"],
        content="Old content",
        example_correct="old_correct",
        example_incorrect="OldIncorrect",
        version=1,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    mock_convention_repository.find_latest_by_logical_key.return_value = existing_conv
    mock_convention_repository.save.side_effect = lambda conv: conv

    updated_content = "Use camelCase for variables."
    updated_convention = convention_service.create_or_update_convention(
        project=sample_convention_data["project"],
        category=sample_convention_data["category"],
        title=sample_convention_data["title"],
        content=updated_content,
        example_correct="newCorrect",
        example_incorrect="new_incorrect"
    )

    assert updated_convention.version == 2
    assert updated_convention.content == updated_content
    mock_convention_repository.save.assert_called_once()
    saved_conv = mock_convention_repository.save.call_args[0][0]
    assert saved_conv.version == 2

def test_get_latest_conventions_for_project(convention_service: ConventionService, mock_convention_repository: Mock):
    mock_conventions = [
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C1", title="T1", content="Content", version=2,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C2", title="T2", content="Content", version=1,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    ]
    mock_convention_repository.find_all_latest_by_project.return_value = mock_conventions

    latest_convs = convention_service.get_latest_conventions_for_project("P1")

    assert latest_convs == mock_conventions
    mock_convention_repository.find_all_latest_by_project.assert_called_once_with("P1")

def test_get_all_unique_project_names(convention_service: ConventionService, mock_convention_repository: Mock):
    mock_project_names = ["ProjectX", "ProjectY"]
    mock_convention_repository.get_all_unique_project_names.return_value = mock_project_names

    project_names = convention_service.get_all_unique_project_names()

    assert project_names == mock_project_names
    mock_convention_repository.get_all_unique_project_names.assert_called_once()

def test_get_all_versions_of_convention(convention_service: ConventionService, mock_convention_repository: Mock):
    mock_versions = [
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C1", title="T1", content="V2", version=2,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C1", title="T1", content="V1", version=1,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    ]
    mock_convention_repository.find_all_versions_by_logical_key.return_value = mock_versions

    all_versions = convention_service.get_all_versions_of_convention("P1", "C1", "T1")

    assert all_versions == mock_versions
    mock_convention_repository.find_all_versions_by_logical_key.assert_called_once_with("P1", "C1", "T1")

def test_soft_delete_convention_by_logical_key(convention_service: ConventionService, mock_convention_repository: Mock):
    mock_convention_repository.soft_delete_all_versions_by_logical_key.return_value = 3

    deleted_count = convention_service.soft_delete_convention_by_logical_key("P1", "C1", "T1")

    assert deleted_count == 3
    mock_convention_repository.soft_delete_all_versions_by_logical_key.assert_called_once_with("P1", "C1", "T1")

def test_get_conventions_by_category_fetches_latest_versions(convention_service: ConventionService, mock_convention_repository: Mock):
    mock_latest_conventions = [
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C1", title="T1", content="V2", version=2,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        ProjectConvention(identifier=uuid.uuid4(), project="P1", category="C1", title="T2", content="V1", version=1,
                          example_correct="", example_incorrect="", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    ]
    mock_convention_repository.find_latest_by_project_and_category.return_value = mock_latest_conventions

    latest_convs_in_category = convention_service.get_conventions_by_category("P1", "C1")

    assert latest_convs_in_category == mock_latest_conventions
    mock_convention_repository.find_latest_by_project_and_category.assert_called_once_with("P1", "C1")
