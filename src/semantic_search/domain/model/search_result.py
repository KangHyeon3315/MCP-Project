from dataclasses import dataclass
from typing import List, Literal, Dict, Any


@dataclass
class DocumentMatch:
    """검색 결과 매치 항목"""
    document_type: Literal["DOMAIN_DOCUMENT", "PROJECT_CONVENTION"]
    document_id: str
    similarity: float
    content: Dict[str, Any]  # 문서 전체 내용


@dataclass
class SearchResult:
    """검색 결과"""
    query: str
    matches: List[DocumentMatch]
    total_count: int
