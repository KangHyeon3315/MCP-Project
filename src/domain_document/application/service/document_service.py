from typing import Optional, List
import uuid
from datetime import datetime, timezone

from src.domain_document.domain.model.document import DomainDocument, DomainProperty, DomainPolicy
from src.domain_document.application.port.output.document_repository_port import DocumentRepositoryPort
from src.domain_document.application.port.input.document_use_case import DocumentUseCase


class DocumentService(DocumentUseCase):
    """
    Implementation of the DocumentUseCase.
    This service contains the core business logic for managing domain documents.
    """

    def __init__(self, document_repository: DocumentRepositoryPort):
        self._repository = document_repository

    def create_or_update_document(self, project: str, service: str, domain: str, summary: str, properties: list, policies: list) -> DomainDocument:
        """
        Creates a new document or a new version of an existing one.
        """
        latest_version = self._repository.find_latest_by_logical_key(
            project=project,
            service=service,
            domain=domain
        )
        
        new_version_number = 1
        if latest_version:
            new_version_number = latest_version.version + 1
        
        new_document = DomainDocument(
            identifier=uuid.uuid4(),
            project=project,
            service=service,
            domain=domain,
            summary=summary,
            version=new_version_number,
            properties=[DomainProperty(**p) for p in properties],
            policies=[DomainPolicy(**p) for p in policies],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return self._repository.save(new_document)

    def get_document_by_full_name(self, project: str, service: str, domain: str, version: int) -> Optional[DomainDocument]:
        """
        Retrieves a specific version of a domain document.
        """
        return self._repository.find_by_full_name(project, service, domain, version)

    def get_document_context(self, identifier: uuid.UUID) -> Optional[dict]:
        """
        Retrieves the full context for a domain, including properties, policies, and relationships.
        This would typically involve calling a specific query or view.
        For now, it retrieves the document and we can imagine it being formatted.
        """
        # In a real implementation, this might call a different repository method
        # that queries the `view_domain_full_context`.
        document = self._repository.find_by_identifier(identifier)
        if not document:
            return None
            
        # Returning the model as a dict for now.
        # The actual view logic would be handled by the adapter or a specific query object.
        return document.model_dump()

    def find_all_latest_by_project(self, project: str) -> List[DomainDocument]:
        """
        Retrieves the latest version of all domain documents for a given project.
        """
        return self._repository.find_all_latest_by_project(project)

    def get_all_unique_project_names(self) -> List[str]:
        """
        Retrieves a list of all unique project names.
        """
        return self._repository.get_all_unique_project_names()

    def get_all_versions_of_document(self, project: str, service: str, domain: str) -> List[DomainDocument]:
        """
        Retrieves all versions of a single document.
        """
        return self._repository.find_all_versions_by_logical_key(project, service, domain)

    def soft_delete_document_by_logical_key(self, project: str, service: str, domain: str) -> int:
        """
        Soft-deletes all versions of a domain document.
        """
        return self._repository.soft_delete_all_versions_by_logical_key(project, service, domain)
