#!/usr/bin/env python3
"""
MCP Server for domain document and project convention management tools.

This server exposes 8 tools for managing domain documents and project conventions:
- read_domain_spec: Read domain data structure and policies
- read_project_conventions: Read project style and architecture rules
- analyze_impact: Analyze impact of requirement changes
- create_or_update_domain_document: Create/update domain document
- create_or_update_project_convention: Create/update project convention
- soft_delete_domain_document: Soft delete domain document
- soft_delete_project_convention: Soft delete project convention
- semantic_search: Search documents using natural language queries
"""

import sys
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file using absolute path
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Import handler functions from the existing handler module
from src.mcp.handler import (
    read_domain_spec as handler_read_domain_spec,
    read_project_conventions as handler_read_project_conventions,
    analyze_impact as handler_analyze_impact,
    create_or_update_domain_document as handler_create_or_update_domain_document,
    create_or_update_project_convention as handler_create_or_update_project_convention,
    soft_delete_domain_document as handler_soft_delete_domain_document,
    soft_delete_project_convention as handler_soft_delete_project_convention,
    semantic_search as handler_semantic_search,
)

# Configure logging to stderr (stdout is used for JSON-RPC messages)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Domain & Convention Manager")

# --- Tool 1: Read Domain Spec ---
@mcp.tool()
def read_domain_spec(
    project_name: str,
    service_name: str,
    domain_name: str,
    version: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Read the data structure and policies for a specific domain.

    Args:
        project_name: The name of the project (e.g., "my-project")
        service_name: The name of the service (e.g., "Auth")
        domain_name: The name of the domain (e.g., "User")
        version: Optional specific version number. If not provided, returns the latest version.

    Returns:
        Dictionary containing the domain document with properties, policies, and dependencies,
        or None if the domain document is not found.
    """
    logger.info(f"Reading domain spec: {project_name}/{service_name}/{domain_name} (version: {version})")
    try:
        result = handler_read_domain_spec(project_name, service_name, domain_name, version)
        logger.info(f"Successfully read domain spec for {domain_name}")
        return result
    except Exception as e:
        logger.error(f"Error reading domain spec: {str(e)}", exc_info=True)
        raise


# --- Tool 2: Read Project Conventions ---
@mcp.tool()
def read_project_conventions(
    project_name: str,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Read project style and architecture rules.

    Args:
        project_name: The name of the project (e.g., "my-project")
        category: Optional category filter (e.g., "NAMING", "ARCHITECTURE", "TESTING")

    Returns:
        List of project convention documents. If category is provided, only conventions
        from that category are returned. Otherwise, all latest conventions are returned.
    """
    logger.info(f"Reading project conventions: {project_name} (category: {category})")
    try:
        result = handler_read_project_conventions(project_name, category)
        logger.info(f"Successfully read {len(result)} conventions")
        return result
    except Exception as e:
        logger.error(f"Error reading project conventions: {str(e)}", exc_info=True)
        raise


# --- Tool 3: Analyze Impact ---
@mcp.tool()
def analyze_impact(
    project_name: str,
    service_name: str,
    domain_name: str
) -> str:
    """
    Analyze the impact of a requirement change by identifying which domains depend on the specified domain.

    Args:
        project_name: The name of the project (e.g., "my-project")
        service_name: The name of the service (e.g., "Auth")
        domain_name: The name of the domain to analyze (e.g., "User")

    Returns:
        A text description of which domains reference the specified domain,
        or a message indicating no dependencies were found.
    """
    logger.info(f"Analyzing impact for: {project_name}/{service_name}/{domain_name}")
    try:
        result = handler_analyze_impact(project_name, service_name, domain_name)
        logger.info(f"Impact analysis complete for {domain_name}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing impact: {str(e)}", exc_info=True)
        raise


# --- Tool 4: Create or Update Domain Document ---
@mcp.tool()
def create_or_update_domain_document(
    project_name: str,
    service_name: str,
    domain_name: str,
    summary: str,
    properties: List[Dict[str, Any]],
    policies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a new domain document or update an existing one (creates a new version).

    Args:
        project_name: The name of the project (e.g., "my-project")
        service_name: The name of the service (e.g., "Auth")
        domain_name: The name of the domain (e.g., "User")
        summary: A brief description of the domain's purpose
        properties: List of domain properties, each with:
            - name: Property name
            - type: Data type (e.g., "String", "Integer")
            - description: Property description
            - is_required: Whether the property is required (boolean)
            - is_immutable: Whether the property is immutable (boolean)
        policies: List of domain policies, each with:
            - category: Policy category (e.g., "PERMISSION", "VALIDATION")
            - subject: Policy subject (e.g., "ADMIN", "USER")
            - content: Policy content description

    Returns:
        The newly created or updated domain document as a dictionary.
    """
    logger.info(f"Creating/updating domain document: {project_name}/{service_name}/{domain_name}")
    try:
        result = handler_create_or_update_domain_document(
            project_name, service_name, domain_name, summary, properties, policies
        )
        logger.info(f"Successfully created/updated domain document for {domain_name}")
        return result
    except Exception as e:
        logger.error(f"Error creating/updating domain document: {str(e)}", exc_info=True)
        raise


# --- Tool 5: Create or Update Project Convention ---
@mcp.tool()
def create_or_update_project_convention(
    project_name: str,
    category: str,
    title: str,
    content: str,
    example_correct: Optional[str] = None,
    example_incorrect: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new project convention or update an existing one (creates a new version).

    Args:
        project_name: The name of the project (e.g., "my-project")
        category: Convention category (e.g., "NAMING", "ARCHITECTURE", "TESTING")
        title: Convention title (e.g., "변수 명명 규칙")
        content: Detailed convention content/rules
        example_correct: Optional example of correct usage
        example_incorrect: Optional example of incorrect usage

    Returns:
        The newly created or updated project convention as a dictionary.
    """
    logger.info(f"Creating/updating project convention: {project_name}/{category}/{title}")
    try:
        result = handler_create_or_update_project_convention(
            project_name, category, title, content, example_correct, example_incorrect
        )
        logger.info(f"Successfully created/updated convention: {title}")
        return result
    except Exception as e:
        logger.error(f"Error creating/updating project convention: {str(e)}", exc_info=True)
        raise


# --- Tool 6: Soft Delete Domain Document ---
@mcp.tool()
def soft_delete_domain_document(
    project_name: str,
    service_name: str,
    domain_name: str
) -> str:
    """
    Soft-delete all versions of a domain document.

    This marks the domain document as deleted without actually removing it from the database,
    allowing for potential recovery.

    Args:
        project_name: The name of the project (e.g., "my-project")
        service_name: The name of the service (e.g., "Auth")
        domain_name: The name of the domain to delete (e.g., "User")

    Returns:
        A message indicating how many records were soft-deleted.
    """
    logger.info(f"Soft-deleting domain document: {project_name}/{service_name}/{domain_name}")
    try:
        result = handler_soft_delete_domain_document(project_name, service_name, domain_name)
        logger.info(f"Successfully soft-deleted domain: {domain_name}")
        return result
    except Exception as e:
        logger.error(f"Error soft-deleting domain document: {str(e)}", exc_info=True)
        raise


# --- Tool 7: Soft Delete Project Convention ---
@mcp.tool()
def soft_delete_project_convention(
    project_name: str,
    category: str,
    title: str
) -> str:
    """
    Soft-delete all versions of a project convention.

    This marks the convention as deleted without actually removing it from the database,
    allowing for potential recovery.

    Args:
        project_name: The name of the project (e.g., "my-project")
        category: Convention category (e.g., "NAMING", "ARCHITECTURE")
        title: Convention title to delete (e.g., "변수 명명 규칙")

    Returns:
        A message indicating how many records were soft-deleted.
    """
    logger.info(f"Soft-deleting project convention: {project_name}/{category}/{title}")
    try:
        result = handler_soft_delete_project_convention(project_name, category, title)
        logger.info(f"Successfully soft-deleted convention: {title}")
        return result
    except Exception as e:
        logger.error(f"Error soft-deleting project convention: {str(e)}", exc_info=True)
        raise


# --- Tool 8: Semantic Search ---
@mcp.tool()
def semantic_search(
    query: str,
    top_k: int = 10,
    similarity_threshold: float = 0.3
) -> Dict[str, Any]:
    """
    Search for domain documents and project conventions using natural language queries.

    This tool uses semantic search (vector similarity) to find relevant documents
    based on the meaning of the query, not just keyword matching.

    Args:
        query: Natural language search query (e.g., "사용자 인증 정책", "변수 명명 규칙")
        top_k: Maximum number of results to return (default: 10)
        similarity_threshold: Minimum similarity score (0.0-1.0) to include in results (default: 0.3)

    Returns:
        Dictionary containing:
        - query: The original search query
        - total_count: Number of results found
        - matches: List of matching documents, each with:
            - document_type: "DOMAIN_DOCUMENT" or "PROJECT_CONVENTION"
            - document_id: Unique identifier
            - similarity: Similarity score (0.0-1.0, higher is better)
            - content: Full document content

    Examples:
        >>> semantic_search("사용자 인증 관련 정책")
        >>> semantic_search("naming conventions", top_k=5, similarity_threshold=0.5)
    """
    logger.info(f"Semantic search: '{query}' (top_k={top_k}, threshold={similarity_threshold})")
    try:
        result = handler_semantic_search(query, top_k, similarity_threshold)
        logger.info(f"Found {result['total_count']} results for query: '{query}'")
        return result
    except Exception as e:
        logger.error(f"Error performing semantic search: {str(e)}", exc_info=True)
        raise


# --- Main Entry Point ---
if __name__ == "__main__":
    logger.info("Starting MCP server for Domain & Convention Manager")
    logger.info("Server running via stdio transport")

    # Run the server via stdio (for Claude Code integration)
    mcp.run()
