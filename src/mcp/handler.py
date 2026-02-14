from typing import List, Dict, Any, Optional
from src.container import Container
from datetime import datetime, timezone

# This file simulates the handlers for the tools that the MCP agent would call.
# In a real MCP integration, these functions would be registered as tools.

# --- Read Tools (Existing) ---
def read_domain_spec(project_name: str, service_name: str, domain_name: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Tool 1: Reads the data structure and policies for a specific domain.
    (Corresponds to `read_domain_spec` in the plan)
    Input: {"project_name": "Ttutta", "service_name": "Auth", "domain_name": "User", "version": 1 (Optional)}
    Output (JSON): DomainDocument model (including properties, policies, dependencies).
    """
    container = Container()
    document_service = container.document_service()
    
    document = None
    if version:
        document = document_service.get_document_by_full_name(
            project=project_name,
            service=service_name,
            domain=domain_name,
            version=version
        )
    else: # If no version specified, get the latest
        document = document_service.find_latest_by_logical_key(
            project=project_name,
            service=service_name,
            domain=domain_name
        )
    
    if document:
        return document.model_dump(mode='json')
        
    return None


def read_project_conventions(project_name: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tool 2: Reads project style and architecture rules.
    (Corresponds to `read_project_conventions` in the plan)
    Input: {"project_name": "Ttutta", "category": "NAMING" (Optional)}
    Output (JSON): List of ProjectConvention models.
    """
    container = Container()
    convention_service = container.convention_service()
    
    if category:
        # NOTE: get_conventions_by_category still fetches all versions.
        # This might need to be updated to fetch only latest.
        conventions = convention_service.get_conventions_by_category(project=project_name, category=category)
    else:
        # This now fetches only the latest versions
        conventions = convention_service.get_latest_conventions_for_project(project=project_name)
        
    return [conv.model_dump(mode='json') for conv in conventions]


def analyze_impact(project_name: str, service_name: str, domain_name: str) -> str:
    """
    Tool 3: Analyzes the impact of a requirement change.
    (Corresponds to `analyze_impact` in the plan)
    Input: {"project_name": "Ttutta", "service_name": "Auth", "domain_name": "User"}
    Output (Text): "User 도메인은 Order, AuthLog 도메인에 의해 참조되고 있습니다."
    """
    # This is a placeholder implementation.
    # A real implementation would query the `domain_relationship` table
    # via the service and repository to find dependencies.
    
    # Simulate fetching the 'used_by' information from the view.
    # A proper implementation would need a service method for this.
    
    # Let's pretend we found some dependencies for the 'User' domain
    if domain_name == "User" and project_name == "Ttutta" and service_name == "Auth":
        return f"{domain_name} 도메인은 Order, AuthLog 도메인에 의해 참조되고 있습니다."
    
    return f"{domain_name} 도메인을 참조하는 다른 도메인을 찾을 수 없습니다."

# --- Create/Update Tools ---
def create_or_update_domain_document(project_name: str, service_name: str, domain_name: str, summary: str, properties: List[Dict[str, Any]], policies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tool 4: Creates a new domain document or a new version of an existing one.
    Input: {
        "project_name": "Ttutta",
        "service_name": "Auth",
        "domain_name": "User",
        "summary": "사용자 계정 및 인증 정보를 관리하는 핵심 도메인",
        "properties": [{"name": "email", "type": "String", "description": "이메일", "is_required": true, "is_immutable": false}],
        "policies": [{"category": "PERMISSION", "subject": "ADMIN", "content": "관리자만 접근 가능"}]
    }
    Output (JSON): The newly created/updated DomainDocument model.
    """
    container = Container()
    document_service = container.document_service()
    
    new_doc = document_service.create_or_update_document(
        project=project_name,
        service=service_name,
        domain=domain_name,
        summary=summary,
        properties=properties,
        policies=policies
    )
    return new_doc.model_dump(mode='json')

def create_or_update_project_convention(project_name: str, category: str, title: str, content: str, example_correct: Optional[str] = None, example_incorrect: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool 5: Creates a new project convention or a new version of an existing one.
    Input: {
        "project_name": "Ttutta",
        "category": "NAMING",
        "title": "변수 명명 규칙",
        "content": "CamelCase를 사용한다.",
        "example_correct": "userName",
        "example_incorrect": "user_name"
    }
    Output (JSON): The newly created/updated ProjectConvention model.
    """
    container = Container()
    convention_service = container.convention_service()
    
    new_conv = convention_service.create_or_update_convention(
        project=project_name,
        category=category,
        title=title,
        content=content,
        example_correct=example_correct,
        example_incorrect=example_incorrect
    )
    return new_conv.model_dump(mode='json')


# --- Delete Tools ---
def soft_delete_domain_document(project_name: str, service_name: str, domain_name: str) -> str:
    """
    Tool 6: Soft-deletes all versions of a domain document.
    Input: {"project_name": "Ttutta", "service_name": "Auth", "domain_name": "User"}
    Output (Text): "N records soft-deleted for domain 'User'."
    """
    container = Container()
    document_service = container.document_service()
    
    affected_rows = document_service.soft_delete_document_by_logical_key(
        project=project_name,
        service=service_name,
        domain=domain_name
    )
    return f"{affected_rows} records soft-deleted for domain '{domain_name}'."

def soft_delete_project_convention(project_name: str, category: str, title: str) -> str:
    """
    Tool 7: Soft-deletes all versions of a project convention.
    Input: {"project_name": "Ttutta", "category": "NAMING", "title": "변수 명명 규칙"}
    Output (Text): "N records soft-deleted for convention '변수 명명 규칙'."
    """
    container = Container()
    convention_service = container.convention_service()

    affected_rows = convention_service.soft_delete_convention_by_logical_key(
        project=project_name,
        category=category,
        title=title
    )
    return f"{affected_rows} records soft-deleted for convention '{title}'."


# --- Semantic Search Tool ---
def semantic_search(query: str, top_k: int = 10, similarity_threshold: float = 0.3) -> Dict[str, Any]:
    """
    Tool 8: Semantic search for domain documents and project conventions.
    Searches using natural language queries and returns relevant documents ranked by similarity.

    Input: {
        "query": "사용자 인증 정책",
        "top_k": 10,  # Optional, default 10
        "similarity_threshold": 0.3  # Optional, default 0.3
    }
    Output (JSON): {
        "query": "사용자 인증 정책",
        "total_count": 5,
        "matches": [
            {
                "document_type": "DOMAIN_DOCUMENT" | "PROJECT_CONVENTION",
                "document_id": "uuid",
                "similarity": 0.85,
                "content": {...}  # Full document content
            },
            ...
        ]
    }
    """
    container = Container()
    search_service = container.semantic_search_service()

    result = search_service.search(
        query=query,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )

    return {
        "query": result.query,
        "total_count": result.total_count,
        "matches": [
            {
                "document_type": match.document_type,
                "document_id": match.document_id,
                "similarity": match.similarity,
                "content": match.content
            }
            for match in result.matches
        ]
    }

