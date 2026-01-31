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

    def create_document(self, project: str, service: str, domain: str, summary: str, properties: list, policies: list, created_at: datetime, updated_at: datetime) -> DomainDocument:
        """
        Creates a new domain document.
        """
        # Here you could add validation logic, e.g., check for duplicates
        
        # For simplicity, creating a new document directly.
        # In a real scenario, you'd map the incoming data to the DomainDocument model.
        
        new_document = DomainDocument(
            identifier=uuid.uuid4(),
            project=project,
            service=service,
            domain=domain,
            summary=summary,
            version=1, # Initial version
            properties=[DomainProperty(**p) for p in properties],
            policies=[DomainPolicy(**p) for p in policies],
            dependencies=[],
            created_at=created_at,
            updated_at=updated_at
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
