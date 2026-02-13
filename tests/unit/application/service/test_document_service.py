import pytest
from unittest.mock import Mock, MagicMock
import uuid
from datetime import datetime, timezone

from src.domain_document.application.service.document_service import DocumentService
from src.domain_document.application.port.output.document_repository_port import DocumentRepositoryPort
from src.domain_document.domain.model.document import DomainDocument, DomainProperty, DomainPolicy, DomainRelationship

@pytest.fixture
def mock_document_repository() -> Mock:
    return Mock(spec=DocumentRepositoryPort)

@pytest.fixture
def document_service(mock_document_repository: Mock) -> DocumentService:
    return DocumentService(document_repository=mock_document_repository)

@pytest.fixture
def sample_document_data():
    return {
        "project": "TestProject",
        "service": "TestService",
        "domain": "TestDomain",
        "summary": "This is a test domain document.",
        "properties": [
            {"name": "id", "description": "Unique ID", "type": "UUID", "is_required": True, "is_immutable": True},
            {"name": "name", "description": "Name", "type": "String", "is_required": True, "is_immutable": False}
        ],
        "policies": [
            {"category": "Retention", "subject": "Data", "content": "Retain for 5 years"},
            {"category": "Access", "subject": "Users", "content": "Only admins can view"}
        ]
    }

def test_create_new_document(document_service: DocumentService, mock_document_repository: Mock, sample_document_data):
    # Mock repository to return the saved document
    mock_document_repository.find_latest_by_logical_key.return_value = None
    mock_document_repository.save.side_effect = lambda doc: doc # Return the document passed to save

    new_document = document_service.create_or_update_document(**sample_document_data)

    assert new_document is not None
    assert isinstance(new_document.identifier, uuid.UUID)
    assert new_document.project == sample_document_data["project"]
    assert new_document.version == 1
    assert len(new_document.properties) == 2
    assert len(new_document.policies) == 2
    mock_document_repository.save.assert_called_once()
    saved_doc = mock_document_repository.save.call_args[0][0]
    assert saved_doc.version == 1

def test_create_new_version_of_document(document_service: DocumentService, mock_document_repository: Mock, sample_document_data):
    # Mock an existing document to simulate an update
    existing_doc = DomainDocument(
        identifier=uuid.uuid4(),
        project=sample_document_data["project"],
        service=sample_document_data["service"],
        domain=sample_document_data["domain"],
        summary="Old summary",
        version=1,
        properties=[], policies=[], dependencies=[],
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    mock_document_repository.find_latest_by_logical_key.return_value = existing_doc
    mock_document_repository.save.side_effect = lambda doc: doc

    updated_summary = "Updated summary for document"
    updated_document = document_service.create_or_update_document(
        project=sample_document_data["project"],
        service=sample_document_data["service"],
        domain=sample_document_data["domain"],
        summary=updated_summary,
        properties=sample_document_data["properties"],
        policies=sample_document_data["policies"]
    )

    assert updated_document.version == 2
    assert updated_document.summary == updated_summary
    mock_document_repository.save.assert_called_once()
    saved_doc = mock_document_repository.save.call_args[0][0]
    assert saved_doc.version == 2

def test_get_document_by_full_name(document_service: DocumentService, mock_document_repository: Mock):
    doc_id = uuid.uuid4()
    mock_document = DomainDocument(
        identifier=doc_id, project="P1", service="S1", domain="D1", summary="Doc 1", version=1,
        properties=[], policies=[], dependencies=[], created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    mock_document_repository.find_by_full_name.return_value = mock_document

    found_doc = document_service.get_document_by_full_name("P1", "S1", "D1", 1)

    assert found_doc == mock_document
    mock_document_repository.find_by_full_name.assert_called_once_with("P1", "S1", "D1", 1)

def test_get_document_context(document_service: DocumentService, mock_document_repository: Mock):
    doc_id = uuid.uuid4()
    mock_document = DomainDocument(
        identifier=doc_id, project="P1", service="S1", domain="D1", summary="Doc 1", version=1,
        properties=[DomainProperty(name="prop1", description="desc", type="str", is_required=True, is_immutable=False)],
        policies=[DomainPolicy(category="Cat1", subject="Sub1", content="Content1")],
        dependencies=[DomainRelationship(target_domain="P2:S2:D2", relation_type="Uses", description="Uses D2")],
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    mock_document_repository.find_by_identifier.return_value = mock_document

    context = document_service.get_document_context(doc_id)

    assert context is not None
    assert str(context["identifier"]) == str(doc_id)
    assert len(context["properties"]) == 1
    assert len(context["policies"]) == 1
    assert len(context["dependencies"]) == 1
    assert context["dependencies"][0]["target_domain"] == "P2:S2:D2"
    mock_document_repository.find_by_identifier.assert_called_once_with(doc_id)

def test_find_all_latest_by_project(document_service: DocumentService, mock_document_repository: Mock):
    mock_documents = [
        DomainDocument(identifier=uuid.uuid4(), project="P1", service="S1", domain="D1", summary="Doc 1", version=2,
                       properties=[], policies=[], dependencies=[], created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        DomainDocument(identifier=uuid.uuid4(), project="P1", service="S2", domain="D2", summary="Doc 2", version=1,
                       properties=[], policies=[], dependencies=[], created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    ]
    mock_document_repository.find_all_latest_by_project.return_value = mock_documents

    latest_docs = document_service.find_all_latest_by_project("P1")

    assert latest_docs == mock_documents
    mock_document_repository.find_all_latest_by_project.assert_called_once_with("P1")

def test_get_all_unique_project_names(document_service: DocumentService, mock_document_repository: Mock):
    mock_project_names = ["ProjectA", "ProjectB"]
    mock_document_repository.get_all_unique_project_names.return_value = mock_project_names

    project_names = document_service.get_all_unique_project_names()

    assert project_names == mock_project_names
    mock_document_repository.get_all_unique_project_names.assert_called_once()

def test_get_all_versions_of_document(document_service: DocumentService, mock_document_repository: Mock):
    mock_versions = [
        DomainDocument(identifier=uuid.uuid4(), project="P1", service="S1", domain="D1", summary="V2", version=2,
                       properties=[], policies=[], dependencies=[], created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        DomainDocument(identifier=uuid.uuid4(), project="P1", service="S1", domain="D1", summary="V1", version=1,
                       properties=[], policies=[], dependencies=[], created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    ]
    mock_document_repository.find_all_versions_by_logical_key.return_value = mock_versions

    all_versions = document_service.get_all_versions_of_document("P1", "S1", "D1")

    assert all_versions == mock_versions
    mock_document_repository.find_all_versions_by_logical_key.assert_called_once_with("P1", "S1", "D1")

def test_soft_delete_document_by_logical_key(document_service: DocumentService, mock_document_repository: Mock):
    mock_document_repository.soft_delete_all_versions_by_logical_key.return_value = 2 # Number of deleted documents

    deleted_count = document_service.soft_delete_document_by_logical_key("P1", "S1", "D1")

    assert deleted_count == 2
    mock_document_repository.soft_delete_all_versions_by_logical_key.assert_called_once_with("P1", "S1", "D1")
