from typing import List, Dict, Any, Optional
from src.container import Container

# This file simulates the handlers for the tools that the MCP agent would call.
# In a real MCP integration, these functions would be registered as tools.

def read_domain_spec(domain_name: str, project_name: str, service_name: str, version: int = 1) -> Optional[Dict[str, Any]]:
    """
    Tool 1: Reads the data structure and policies for a specific domain.
    (Corresponds to `read_domain_spec` in the plan)
    """
    container = Container()
    document_service = container.document_service()
    
    # Note: The service method gets by full name, so we need more than just domain_name
    document = document_service.get_document_by_full_name(
        project=project_name,
        service=service_name,
        domain=domain_name,
        version=version
    )
    
    if document:
        # The plan's output format is slightly different from the Pydantic model.
        # This is where the final transformation for the LLM would happen.
        return document.model_dump()
        
    return None


def read_project_conventions(project_name: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tool 2: Reads project style and architecture rules.
    (Corresponds to `read_project_conventions` in the plan)
    """
    container = Container()
    convention_service = container.convention_service()
    
    if category:
        conventions = convention_service.get_conventions_by_category(project=project_name, category=category)
    else:
        conventions = convention_service.get_conventions_for_project(project=project_name)
        
    return [conv.model_dump() for conv in conventions]


def analyze_impact(domain_name: str, project_name: str, service_name: str) -> str:
    """
    Tool 3: Analyzes the impact of a requirement change.
    (Corresponds to `analyze_impact` in the plan)
    """
    # This is a placeholder implementation.
    # A real implementation would query the `domain_relationship` table
    # via the service and repository to find dependencies.
    
    # Simulate fetching the 'used_by' information from the view.
    # A proper implementation would need a service method for this.
    
    # Let's pretend we found some dependencies for the 'User' domain
    if domain_name == "User" and project_name == "Ttutta":
        return f"{domain_name} 도메인은 Order, AuthLog 도메인에 의해 참조되고 있습니다."
    
    return f"{domain_name} 도메인을 참조하는 다른 도메인을 찾을 수 없습니다."

