from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from typing import List

from src.container import Container
from src.project_convention.application.port.input.convention_use_case import ConventionUseCase
from src.project_convention.domain.model.convention import ProjectConvention

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
