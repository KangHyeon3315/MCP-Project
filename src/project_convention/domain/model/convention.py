import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectConvention(BaseModel):
    """
    ProjectConvention Model
    """
    identifier: uuid.UUID
    project: str = Field(..., description="프로젝트명")
    category: str = Field(..., description="컨벤션 분류")
    title: str = Field(..., description="규칙 제목")
    version: int = Field(..., description="버전 번호")
    content: str = Field(..., description="규칙 상세 내용")
    example_correct: Optional[str] = Field(None, description="올바른 예시")
    example_incorrect: Optional[str] = Field(None, description="잘못된 예시")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
