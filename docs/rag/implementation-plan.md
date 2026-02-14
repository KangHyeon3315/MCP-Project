# RAG 기능 추가 구현 계획

## 1. 개요

### 목적
MCP 도구에 시맨틱 검색(Semantic Search) 기능을 추가하여 AI Agent가 자연어 질문으로 관련 도메인 문서와 프로젝트 컨벤션을 찾을 수 있도록 합니다.

### 예시 질문
- "사용자 인증과 권한 관련 정책이 뭐야?"
- "변수 명명 규칙은 어떻게 돼?"
- "User 도메인의 필수 속성은?"

### 기술 스택
- **벡터 DB**: PostgreSQL + pgvector (이미 설치됨)
- **임베딩 모델**: sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
  - 384차원 벡터
  - 한국어 지원
  - 로컬 실행 (API 키 불필요)
  - 모델 크기: ~120MB
- **인터페이스**: MCP Tool (`semantic_search`) + 자동 임베딩 생성

---

## 2. 아키텍처 설계

### 2.1 데이터베이스 변경

#### 기존 테이블에 embedding 컬럼 추가

**장점**:
- 데이터 일관성 유지 (문서와 임베딩이 항상 함께)
- JOIN 불필요
- 간단한 아키텍처
- soft-delete 시 임베딩도 자동 관리

**마이그레이션**:
```sql
-- migrations/001_add_embedding_columns.sql

-- domain_document 테이블에 embedding 컬럼 추가
ALTER TABLE domain_document
ADD COLUMN embedding vector(384);

-- project_convention 테이블에 embedding 컬럼 추가
ALTER TABLE project_convention
ADD COLUMN embedding vector(384);

-- 벡터 유사도 검색 인덱스 (HNSW)
CREATE INDEX idx_domain_document_embedding
ON domain_document USING hnsw (embedding vector_cosine_ops)
WHERE embedding IS NOT NULL;

CREATE INDEX idx_project_convention_embedding
ON project_convention USING hnsw (embedding vector_cosine_ops)
WHERE embedding IS NOT NULL;
```

### 2.2 디렉토리 구조

```
src/semantic_search/
├── domain/model/
│   ├── __init__.py
│   └── search_result.py              # SearchResult, DocumentMatch 도메인 모델
├── application/
│   ├── port/
│   │   ├── __init__.py
│   │   └── output/
│   │       ├── __init__.py
│   │       └── embedding_port.py      # 임베딩 생성 인터페이스
│   └── service/
│       ├── __init__.py
│       ├── semantic_search_service.py # 검색 비즈니스 로직
│       └── embedding_service.py       # 임베딩 관리 로직
└── adapter/
    ├── __init__.py
    └── output/
        ├── __init__.py
        └── embedding/
            ├── __init__.py
            └── sentence_transformer_adapter.py  # 임베딩 구현체
```

### 2.3 데이터 흐름

#### 임베딩 자동 생성
```
DocumentService.create_or_update_document()
    ↓
Repository.save() → 문서 저장 완료
    ↓
EmbeddingService.create_embedding_for_document()
    ↓
텍스트 생성: summary + properties + policies 조합
    ↓
SentenceTransformerAdapter.generate_embedding()
    ↓
문서의 embedding 컬럼 업데이트
Repository.update_embedding()
```

#### 시맨틱 검색
```
MCP Tool: semantic_search(query="사용자 인증 정책")
    ↓
SemanticSearchService.semantic_search()
    ↓
1. 쿼리 임베딩 생성
2. DomainDocumentRepository.semantic_search() 호출
3. ProjectConventionRepository.semantic_search() 호출
4. 결과 병합 및 유사도 순 정렬
5. SearchResult 반환 (문서 + 유사도 점수)
```

---

## 3. 구현 단계

### Phase 1: 데이터베이스 및 의존성 설정

#### 1.1 의존성 추가
```toml
# pyproject.toml
dependencies = [
    # ... 기존 의존성 ...
    "pgvector>=0.3.6,<0.4.0",
    "sentence-transformers>=3.3.1,<4.0.0",
]
```

#### 1.2 마이그레이션 실행
```bash
# 마이그레이션 스크립트 생성
touch migrations/001_add_embedding_columns.sql

# 마이그레이션 실행 스크립트 작성 (필요시)
python scripts/run_migrations.py
```

#### 1.3 엔티티 수정
```python
# src/domain_document/adapter/output/persistence/entity.py
from pgvector.sqlalchemy import Vector

class DomainDocumentEntity(Base):
    # ... 기존 컬럼들 ...
    embedding = Column(Vector(384), nullable=True)
```

```python
# src/project_convention/adapter/output/persistence/entity.py
from pgvector.sqlalchemy import Vector

class ProjectConventionEntity(Base):
    # ... 기존 컬럼들 ...
    embedding = Column(Vector(384), nullable=True)
```

### Phase 2: Semantic Search 레이어 구현

#### 2.1 도메인 모델 정의
```python
# src/semantic_search/domain/model/search_result.py

from dataclasses import dataclass
from typing import List, Literal

@dataclass
class DocumentMatch:
    """검색 결과 매치 항목"""
    document_type: Literal["DOMAIN_DOCUMENT", "PROJECT_CONVENTION"]
    document_id: str
    similarity: float
    content: dict  # 문서 전체 내용

@dataclass
class SearchResult:
    """검색 결과"""
    query: str
    matches: List[DocumentMatch]
    total_count: int
```

#### 2.2 Port 인터페이스 정의
```python
# src/semantic_search/application/port/output/embedding_port.py

from abc import ABC, abstractmethod
from typing import List

class EmbeddingPort(ABC):
    """임베딩 생성 인터페이스"""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환"""
        pass
```

#### 2.3 Embedding Adapter 구현
```python
# src/semantic_search/adapter/output/embedding/sentence_transformer_adapter.py

from sentence_transformers import SentenceTransformer
from typing import List
from ....application.port.output.embedding_port import EmbeddingPort

class SentenceTransformerAdapter(EmbeddingPort):
    """Sentence Transformers 기반 임베딩 어댑터"""

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self):
        self._model = None  # 지연 로딩

    def _load_model(self):
        """모델 지연 로딩"""
        if self._model is None:
            self._model = SentenceTransformer(self.MODEL_NAME)

    def generate_embedding(self, text: str) -> List[float]:
        """텍스트를 384차원 벡터로 변환"""
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
```

#### 2.4 Embedding Service 구현
```python
# src/semantic_search/application/service/embedding_service.py

from typing import Optional
from ...domain_document.domain.model.domain_document import DomainDocument
from ...project_convention.domain.model.project_convention import ProjectConvention
from ..port.output.embedding_port import EmbeddingPort

class EmbeddingService:
    """임베딩 생성 및 관리 서비스"""

    def __init__(
        self,
        embedding_adapter: EmbeddingPort,
        domain_repository,
        convention_repository
    ):
        self._embedding_adapter = embedding_adapter
        self._domain_repo = domain_repository
        self._convention_repo = convention_repository

    def create_embedding_for_document(self, document: DomainDocument) -> None:
        """도메인 문서에 대한 임베딩 생성 및 저장"""
        text = self._create_document_text(document)
        embedding = self._embedding_adapter.generate_embedding(text)
        self._domain_repo.update_embedding(document.identifier, embedding)

    def create_embedding_for_convention(self, convention: ProjectConvention) -> None:
        """컨벤션에 대한 임베딩 생성 및 저장"""
        text = self._create_convention_text(convention)
        embedding = self._embedding_adapter.generate_embedding(text)
        self._convention_repo.update_embedding(convention.identifier, embedding)

    def _create_document_text(self, doc: DomainDocument) -> str:
        """도메인 문서를 검색 가능한 텍스트로 변환"""
        parts = [
            f"도메인: {doc.domain}",
            f"프로젝트: {doc.project}",
            f"서비스: {doc.service}",
            f"요약: {doc.summary}",
        ]

        if doc.properties:
            props = ", ".join([
                f"{p.name}({p.type}): {p.description}"
                for p in doc.properties
            ])
            parts.append(f"속성: {props}")

        if doc.policies:
            policies = ", ".join([
                f"{p.category} - {p.content}"
                for p in doc.policies
            ])
            parts.append(f"정책: {policies}")

        return " | ".join(parts)

    def _create_convention_text(self, conv: ProjectConvention) -> str:
        """컨벤션을 검색 가능한 텍스트로 변환"""
        parts = [
            f"컨벤션: {conv.title}",
            f"분류: {conv.category}",
            f"내용: {conv.content}",
        ]

        if conv.example_correct:
            parts.append(f"올바른 예시: {conv.example_correct}")

        if conv.example_incorrect:
            parts.append(f"잘못된 예시: {conv.example_incorrect}")

        return " | ".join(parts)
```

### Phase 3: Repository 확장

#### 3.1 DomainDocumentRepository 확장
```python
# src/domain_document/adapter/output/persistence/repository.py

from typing import List, Tuple
from sqlalchemy import text

class DomainDocumentRepository:
    # ... 기존 메서드들 ...

    def update_embedding(self, document_id: str, embedding: List[float]) -> None:
        """문서의 임베딩 업데이트"""
        self._session.execute(
            text("""
                UPDATE domain_document
                SET embedding = :embedding::vector,
                    updated_at = NOW()
                WHERE identifier = :document_id
            """),
            {"document_id": document_id, "embedding": embedding}
        )
        self._session.commit()

    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> List[Tuple[DomainDocument, float]]:
        """벡터 유사도 검색"""
        query = text("""
            SELECT *,
                   1 - (embedding <=> :query_vector::vector) as similarity
            FROM domain_document
            WHERE deleted_at IS NULL
              AND embedding IS NOT NULL
              AND 1 - (embedding <=> :query_vector::vector) > :threshold
            ORDER BY embedding <=> :query_vector::vector
            LIMIT :top_k
        """)

        result = self._session.execute(
            query,
            {
                "query_vector": query_embedding,
                "threshold": similarity_threshold,
                "top_k": top_k
            }
        )

        # 결과를 DomainDocument 객체로 변환
        results = []
        for row in result:
            entity = self._row_to_entity(row)
            document = self._entity_to_domain(entity)
            similarity = row.similarity
            results.append((document, similarity))

        return results
```

#### 3.2 ProjectConventionRepository 확장
```python
# src/project_convention/adapter/output/persistence/repository.py
# 동일한 패턴으로 update_embedding, semantic_search 메서드 추가
```

### Phase 4: Semantic Search Service 구현

```python
# src/semantic_search/application/service/semantic_search_service.py

from typing import List
from ..domain.model.search_result import SearchResult, DocumentMatch
from ..port.output.embedding_port import EmbeddingPort

class SemanticSearchService:
    """시맨틱 검색 서비스"""

    def __init__(
        self,
        embedding_adapter: EmbeddingPort,
        domain_repository,
        convention_repository
    ):
        self._embedding_adapter = embedding_adapter
        self._domain_repo = domain_repository
        self._convention_repo = convention_repository

    def search(
        self,
        query: str,
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> SearchResult:
        """자연어 쿼리로 시맨틱 검색"""
        # 1. 쿼리 임베딩 생성
        query_embedding = self._embedding_adapter.generate_embedding(query)

        # 2. 두 테이블 모두 검색
        domain_results = self._domain_repo.semantic_search(
            query_embedding, top_k, similarity_threshold
        )
        convention_results = self._convention_repo.semantic_search(
            query_embedding, top_k, similarity_threshold
        )

        # 3. 결과 병합 및 정렬
        matches = []

        for doc, similarity in domain_results:
            matches.append(DocumentMatch(
                document_type="DOMAIN_DOCUMENT",
                document_id=str(doc.identifier),
                similarity=similarity,
                content=self._document_to_dict(doc)
            ))

        for conv, similarity in convention_results:
            matches.append(DocumentMatch(
                document_type="PROJECT_CONVENTION",
                document_id=str(conv.identifier),
                similarity=similarity,
                content=self._convention_to_dict(conv)
            ))

        # 유사도 순으로 정렬 후 top_k개만 선택
        matches.sort(key=lambda x: x.similarity, reverse=True)
        matches = matches[:top_k]

        return SearchResult(
            query=query,
            matches=matches,
            total_count=len(matches)
        )
```

### Phase 5: 기존 서비스 통합

#### 5.1 DocumentService 수정
```python
# src/domain_document/application/service/document_service.py

class DocumentService:
    def __init__(
        self,
        document_repository,
        embedding_service=None  # Optional
    ):
        self._repository = document_repository
        self._embedding_service = embedding_service

    def create_or_update_document(self, ...) -> DomainDocument:
        # ... 기존 로직 ...
        saved_document = self._repository.save(new_document)

        # 임베딩 자동 생성
        if self._embedding_service:
            try:
                self._embedding_service.create_embedding_for_document(saved_document)
            except Exception as e:
                logging.error(f"Failed to create embedding: {e}")
                # 임베딩 실패해도 문서 저장은 성공으로 처리

        return saved_document
```

#### 5.2 ConventionService 수정
```python
# src/project_convention/application/service/convention_service.py
# 동일한 패턴으로 embedding_service 통합
```

### Phase 6: Container 설정

```python
# src/container.py

from dependency_injector import containers, providers
from .semantic_search.adapter.output.embedding.sentence_transformer_adapter import SentenceTransformerAdapter
from .semantic_search.application.service.embedding_service import EmbeddingService
from .semantic_search.application.service.semantic_search_service import SemanticSearchService

class Container(containers.DeclarativeContainer):
    # ... 기존 설정 ...

    # Embedding Adapter (Singleton - 모델을 한 번만 로드)
    embedding_adapter = providers.Singleton(
        SentenceTransformerAdapter
    )

    # Embedding Service
    embedding_service = providers.Factory(
        EmbeddingService,
        embedding_adapter=embedding_adapter,
        domain_repository=domain_document_repository,
        convention_repository=project_convention_repository
    )

    # Semantic Search Service
    semantic_search_service = providers.Factory(
        SemanticSearchService,
        embedding_adapter=embedding_adapter,
        domain_repository=domain_document_repository,
        convention_repository=project_convention_repository
    )

    # 기존 서비스에 embedding_service 주입
    document_service = providers.Factory(
        DocumentService,
        document_repository=domain_document_repository,
        embedding_service=embedding_service
    )

    convention_service = providers.Factory(
        ConventionService,
        convention_repository=project_convention_repository,
        embedding_service=embedding_service
    )
```

### Phase 7: MCP Handler 추가

```python
# src/mcp/handler.py

def semantic_search(
    query: str,
    top_k: int = 10,
    similarity_threshold: float = 0.3
) -> dict:
    """
    자연어 쿼리로 도메인 문서 및 컨벤션 검색

    Args:
        query: 검색 쿼리 (예: "사용자 인증 정책")
        top_k: 최대 반환 결과 수
        similarity_threshold: 최소 유사도 임계값 (0.0 ~ 1.0)

    Returns:
        검색 결과 (문서 목록 + 유사도 점수)
    """
    container = Container()
    search_service = container.semantic_search_service()

    result = search_service.search(query, top_k, similarity_threshold)

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
```

```python
# mcp_server.py

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    # ... 기존 툴들 ...

    if name == "semantic_search":
        result = handler.semantic_search(
            query=arguments["query"],
            top_k=arguments.get("top_k", 10),
            similarity_threshold=arguments.get("similarity_threshold", 0.3)
        )
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
```

### Phase 8: 기존 데이터 마이그레이션

```python
# scripts/generate_embeddings_batch.py

from src.container import Container
from tqdm import tqdm

def generate_all_embeddings():
    """기존 모든 문서 및 컨벤션에 대한 임베딩 생성"""
    container = Container()

    domain_repo = container.domain_document_repository()
    convention_repo = container.project_convention_repository()
    embedding_service = container.embedding_service()

    # 도메인 문서 임베딩 생성
    print("Generating embeddings for domain documents...")
    documents = domain_repo.find_all()
    for doc in tqdm(documents):
        try:
            if doc.embedding is None:  # 임베딩이 없는 경우만
                embedding_service.create_embedding_for_document(doc)
        except Exception as e:
            print(f"Failed to create embedding for {doc.identifier}: {e}")

    # 컨벤션 임베딩 생성
    print("Generating embeddings for conventions...")
    conventions = convention_repo.find_all()
    for conv in tqdm(conventions):
        try:
            if conv.embedding is None:
                embedding_service.create_embedding_for_convention(conv)
        except Exception as e:
            print(f"Failed to create embedding for {conv.identifier}: {e}")

    print("Done!")

if __name__ == "__main__":
    generate_all_embeddings()
```

---

## 4. 검증 방법

### 4.1 데이터베이스 확인

```bash
# 컬럼 추가 확인
psql -U root -h 100.115.231.5 -p 31002 -d postgres \
  -c "\d domain_document"

# 인덱스 생성 확인
psql -U root -h 100.115.231.5 -p 31002 -d postgres \
  -c "\di idx_domain_document_embedding"
```

### 4.2 임베딩 자동 생성 테스트

```python
# 새 도메인 생성 후 임베딩 확인
from src.mcp.handler import create_or_update_domain_document

result = create_or_update_domain_document(
    project_name="TestProject",
    service_name="TestService",
    domain_name="TestDomain",
    summary="테스트 도메인입니다",
    properties=[{
        "name": "id",
        "type": "UUID",
        "description": "식별자",
        "is_required": True,
        "is_immutable": True
    }],
    policies=[{
        "category": "PERMISSION",
        "subject": "USER",
        "content": "모든 사용자 접근 가능"
    }]
)

# DB에서 embedding 컬럼 확인
# SELECT identifier, embedding IS NOT NULL as has_embedding FROM domain_document;
```

### 4.3 시맨틱 검색 테스트

```python
from src.mcp.handler import semantic_search

# 테스트 검색
results = semantic_search(
    query="사용자 인증 정책",
    top_k=5,
    similarity_threshold=0.3
)

print(f"검색 결과: {results['total_count']}개")
for match in results['matches']:
    print(f"- {match['document_type']}: {match['similarity']:.2f}")
```

### 4.4 배치 임베딩 생성

```bash
poetry run python scripts/generate_embeddings_batch.py
```

---

## 5. 파일 목록

### 새로 생성할 파일 (14개)

**마이그레이션 & 스크립트**:
- `migrations/001_add_embedding_columns.sql`
- `scripts/generate_embeddings_batch.py`

**도메인 모델**:
- `src/semantic_search/domain/model/__init__.py`
- `src/semantic_search/domain/model/search_result.py`

**Port 인터페이스**:
- `src/semantic_search/application/port/__init__.py`
- `src/semantic_search/application/port/output/__init__.py`
- `src/semantic_search/application/port/output/embedding_port.py`

**서비스**:
- `src/semantic_search/application/service/__init__.py`
- `src/semantic_search/application/service/semantic_search_service.py`
- `src/semantic_search/application/service/embedding_service.py`

**어댑터**:
- `src/semantic_search/adapter/__init__.py`
- `src/semantic_search/adapter/output/__init__.py`
- `src/semantic_search/adapter/output/embedding/__init__.py`
- `src/semantic_search/adapter/output/embedding/sentence_transformer_adapter.py`

### 수정할 파일 (6개)

1. `pyproject.toml` - 의존성 추가
2. `src/domain_document/adapter/output/persistence/entity.py` - embedding 컬럼 추가
3. `src/project_convention/adapter/output/persistence/entity.py` - embedding 컬럼 추가
4. `src/domain_document/adapter/output/persistence/repository.py` - 벡터 검색 메서드 추가
5. `src/project_convention/adapter/output/persistence/repository.py` - 벡터 검색 메서드 추가
6. `src/container.py` - DI 설정
7. `src/domain_document/application/service/document_service.py` - 임베딩 자동 생성 통합
8. `src/project_convention/application/service/convention_service.py` - 임베딩 자동 생성 통합
9. `src/mcp/handler.py` - semantic_search 핸들러 추가
10. `mcp_server.py` - MCP Tool 등록

---

## 6. 주요 기술 세부사항

### 6.1 벡터 검색 쿼리

```sql
SELECT *,
       1 - (embedding <=> :query_vector::vector) as similarity
FROM domain_document
WHERE deleted_at IS NULL
  AND embedding IS NOT NULL
  AND 1 - (embedding <=> :query_vector::vector) > :threshold
ORDER BY embedding <=> :query_vector::vector
LIMIT :top_k
```

- `<=>`: Cosine distance operator (pgvector)
- `1 - distance`: Similarity score (0~1)
- HNSW 인덱스로 빠른 검색 (O(log n))

### 6.2 에러 처리 전략

**임베딩 생성 실패**:
- 로그만 기록, 문서 저장은 성공 처리
- 이유: 임베딩은 부가 기능이므로 핵심 기능을 방해하지 않음
- 복구: 배치 스크립트로 누락된 임베딩 보완

**검색 실패**:
- 예외 발생 및 로그 기록
- 사용자에게 에러 메시지 반환

### 6.3 성능 최적화

**모델 로딩**:
- Singleton 패턴으로 1회만 로드
- 지연 로딩으로 서버 시작 시간 최소화

**벡터 검색**:
- HNSW 인덱스 사용 (Approximate Nearest Neighbor)
- similarity_threshold로 후보 필터링

**배치 처리**:
- 한 번에 100개씩 처리
- tqdm으로 진행 상황 표시

---

## 7. 예상 리스크 및 대응

### 리스크 1: 첫 실행 시 모델 다운로드 지연
**대응**: 사전 다운로드 안내, 지연 로딩

### 리스크 2: 메모리 사용량 증가 (~120MB)
**대응**: Singleton 패턴, 경량 모델 사용

### 리스크 3: 대량 배치 처리 시간
**대응**: 배치 크기 조정, 진행 상황 표시

### 리스크 4: 임베딩 생성 실패 시 데이터 불일치
**대응**: 실패 로그 기록, 배치 스크립트로 주기적 보완

---

## 8. 예상 일정

- Phase 1 (DB & 의존성): 0.5일
- Phase 2 (Semantic Search 레이어): 1.5일
- Phase 3 (Repository 확장): 1일
- Phase 4 (Search Service): 1일
- Phase 5 (기존 서비스 통합): 1일
- Phase 6 (Container 설정): 0.5일
- Phase 7 (MCP Handler): 0.5일
- Phase 8 (데이터 마이그레이션): 0.5일

**총 예상**: 6-7일
