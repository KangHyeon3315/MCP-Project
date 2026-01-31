from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from typing import List, Optional

from src.container import Container
from src.project_convention.application.port.input.convention_use_case import ConventionUseCase
from src.project_convention.domain.model.convention import ProjectConvention
from src.domain_document.application.port.input.document_use_case import DocumentUseCase
from src.domain_document.domain.model.document import DomainDocument


router = APIRouter()

@router.get("/conventions/{project_name}", response_model=List[ProjectConvention])
@inject
def get_project_conventions(
    project_name: str,
    convention_service: ConventionUseCase = Depends(Provide[Container.convention_service]),
):
    """
    Retrieves all conventions for a given project.
    """
    conventions = convention_service.get_conventions_for_project(project=project_name)
    return conventions

@router.get("/domains/{project_name}/{service_name}/{domain_name}", response_model=DomainDocument)
@inject
def get_domain_specification(
    project_name: str,
    service_name: str,
    domain_name: str,
    version: Optional[int] = 1,
    document_service: DocumentUseCase = Depends(Provide[Container.document_service]),
):
    """
    Retrieves the specification for a specific domain.
    """
    document = document_service.get_document_by_full_name(
        project=project_name,
        service=service_name,
        domain=domain_name,
        version=version
    )
    if not document:
        raise HTTPException(status_code=404, detail="Domain document not found")
    return document
