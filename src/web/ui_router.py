from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from typing import Optional

from src.container import Container
from src.project_convention.application.port.input.convention_use_case import ConventionUseCase
from src.domain_document.application.port.input.document_use_case import DocumentUseCase

# Configure templates
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/mcp")

@router.get("/", response_class=HTMLResponse)
@inject
def get_project_list_page(
    request: Request,
    document_service: DocumentUseCase = Depends(Provide[Container.document_service]),
    convention_service: ConventionUseCase = Depends(Provide[Container.convention_service]),
):
    """
    Renders the home page with a list of all unique projects.
    """
    doc_projects = document_service.get_all_unique_project_names()
    conv_projects = convention_service.get_all_unique_project_names()

    # Combine and get unique project names
    project_names = sorted(list(set(doc_projects + conv_projects)))

    return templates.TemplateResponse(
        "project_list.html",
        {"request": request, "projects": project_names}
    )

@router.get("/projects/{project_name}", response_class=HTMLResponse)
@inject
def get_project_detail_page(
    request: Request,
    project_name: str,
    service_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    document_service: DocumentUseCase = Depends(Provide[Container.document_service]),
    convention_service: ConventionUseCase = Depends(Provide[Container.convention_service]),
):
    """
    Renders the detail page for a project, with optional filtering.
    """
    # Fetch only the latest versions of all data for the project
    all_domains = document_service.find_all_latest_by_project(project=project_name)
    all_conventions = convention_service.get_latest_conventions_for_project(project=project_name)

    # Get available filter options
    available_services = sorted(list(set([d.service for d in all_domains])))
    available_categories = sorted(list(set([c.category for c in all_conventions])))

    # Apply filters if they are provided
    filtered_domains = [d for d in all_domains if not service_filter or d.service == service_filter]
    filtered_conventions = [c for c in all_conventions if not category_filter or c.category == category_filter]

    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "project_name": project_name,
            "domains": filtered_domains,
            "conventions": filtered_conventions,
            "available_services": available_services,
            "available_categories": available_categories,
            "current_service_filter": service_filter,
            "current_category_filter": category_filter,
        }
    )


@router.get("/domains/{project_name}/{service_name}/{domain_name}", response_class=HTMLResponse)
@inject
def get_domain_detail_page(
    request: Request,
    project_name: str,
    service_name: str,
    domain_name: str,
    version: Optional[int] = None, # Version is now an optional query param
    document_service: DocumentUseCase = Depends(Provide[Container.document_service]),
):
    """
    Renders the detail page for a specific domain.
    If no version is specified, it shows the latest version.
    """
    # Fetch all versions to populate the dropdown
    all_versions = document_service.get_all_versions_of_document(
        project=project_name,
        service=service_name,
        domain=domain_name
    )
    if not all_versions:
        raise HTTPException(status_code=404, detail="Domain document not found")

    # Determine which document to display
    if version:
        document_to_display = next((v for v in all_versions if v.version == version), None)
    else:
        document_to_display = all_versions[0] # The list is ordered by version desc

    if not document_to_display:
        raise HTTPException(status_code=404, detail=f"Version {version} not found for this domain")

    return templates.TemplateResponse(
        "domain_detail.html",
        {"request": request, "domain": document_to_display, "all_versions": all_versions}
    )

@router.get("/conventions/{project_name}/{category}/{title}", response_class=HTMLResponse)
@inject
def get_convention_detail_page(
    request: Request,
    project_name: str,
    category: str,
    title: str,
    version: Optional[int] = None,
    convention_service: ConventionUseCase = Depends(Provide[Container.convention_service]),
):
    """
    Renders the detail page for a specific convention.
    If no version is specified, it shows the latest version.
    """
    all_versions = convention_service.get_all_versions_of_convention(
        project=project_name,
        category=category,
        title=title
    )
    if not all_versions:
        raise HTTPException(status_code=404, detail="Convention not found")

    if version:
        convention_to_display = next((v for v in all_versions if v.version == version), None)
    else:
        convention_to_display = all_versions[0]

    if not convention_to_display:
        raise HTTPException(status_code=404, detail=f"Version {version} not found for this convention")

    return templates.TemplateResponse(
        "convention_detail.html",
        {"request": request, "convention": convention_to_display, "all_versions": all_versions}
    )
