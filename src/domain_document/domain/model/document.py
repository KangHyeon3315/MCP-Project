import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class DomainProperty(BaseModel):
    name: str = Field(..., description="속성 이름 (e.g., 'email')")
    description: str = Field(..., description="속성 설명 (e.g., '사용자 이메일')")
    type: str = Field(..., description="데이터 타입 (e.g., 'String', 'UUID', 'Enum')")
    is_required: bool = Field(..., description="필수 여부")
    is_immutable: bool = Field(..., description="불변 여부")

    model_config = ConfigDict(from_attributes=True)


class DomainPolicy(BaseModel):
    category: str = Field(..., description="정책 분류 (e.g., 'PERMISSION', 'LIFECYCLE')")
    subject: Optional[str] = Field(None, description="정책 주체 (e.g., 'ADMIN', 'MEMBER')")
    content: str = Field(..., description="정책 상세 내용")

    model_config = ConfigDict(from_attributes=True)


class DomainRelationship(BaseModel):
    target_domain: str = Field(..., description="관계 대상 도메인")
    relation_type: str = Field(..., description="관계 유형 (e.g., 'DEPENDENCY')")
    description: str = Field(..., description="관계 설명")
    impact_description: Optional[str] = Field(None, description="영향 분석")

    model_config = ConfigDict(from_attributes=True)


class DomainDocument(BaseModel):
    """
    DomainDocument Aggregate Root
    """
    identifier: uuid.UUID
    project: str
    service: str
    domain: str
    summary: str
    version: int
    
    properties: List[DomainProperty] = Field([], description="도메인 속성 목록")
    policies: List[DomainPolicy] = Field([], description="도메인 정책 목록")
    
    # 이 모델을 기준으로 '내가 참조하는' 다른 도메인들
    dependencies: List[DomainRelationship] = Field([], description="의존성 목록 (Source -> Target)")
    
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
        
