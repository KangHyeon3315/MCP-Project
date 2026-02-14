# RAG 기능 구현 TODO

## Phase 1: 데이터베이스 및 의존성 설정

### 1.1 의존성 추가
- [ ] `pyproject.toml`에 `pgvector>=0.3.6,<0.4.0` 추가
- [ ] `pyproject.toml`에 `sentence-transformers>=3.3.1,<4.0.0` 추가
- [ ] `poetry install` 실행하여 의존성 설치

### 1.2 마이그레이션 생성 및 실행
- [ ] `migrations/001_add_embedding_columns.sql` 파일 생성
- [ ] `domain_document` 테이블에 `embedding vector(384)` 컬럼 추가 SQL 작성
- [ ] `project_convention` 테이블에 `embedding vector(384)` 컬럼 추가 SQL 작성
- [ ] `idx_domain_document_embedding` HNSW 인덱스 생성 SQL 작성
- [ ] `idx_project_convention_embedding` HNSW 인덱스 생성 SQL 작성
- [ ] 마이그레이션 실행 (psql 또는 스크립트 사용)

### 1.3 엔티티 수정
- [ ] `src/domain_document/adapter/output/persistence/entity.py` 수정
  - [ ] `from pgvector.sqlalchemy import Vector` import 추가
  - [ ] `DomainDocumentEntity`에 `embedding = Column(Vector(384), nullable=True)` 추가
- [ ] `src/project_convention/adapter/output/persistence/entity.py` 수정
  - [ ] `from pgvector.sqlalchemy import Vector` import 추가
  - [ ] `ProjectConventionEntity`에 `embedding = Column(Vector(384), nullable=True)` 추가

---

## Phase 2: Semantic Search 레이어 구현

### 2.1 디렉토리 구조 생성
- [ ] `src/semantic_search/` 디렉토리 생성
- [ ] `src/semantic_search/domain/` 디렉토리 생성
- [ ] `src/semantic_search/domain/model/` 디렉토리 생성
- [ ] `src/semantic_search/application/` 디렉토리 생성
- [ ] `src/semantic_search/application/port/` 디렉토리 생성
- [ ] `src/semantic_search/application/port/output/` 디렉토리 생성
- [ ] `src/semantic_search/application/service/` 디렉토리 생성
- [ ] `src/semantic_search/adapter/` 디렉토리 생성
- [ ] `src/semantic_search/adapter/output/` 디렉토리 생성
- [ ] `src/semantic_search/adapter/output/embedding/` 디렉토리 생성

### 2.2 도메인 모델 구현
- [ ] `src/semantic_search/domain/model/__init__.py` 생성
- [ ] `src/semantic_search/domain/model/search_result.py` 생성
  - [ ] `DocumentMatch` 데이터클래스 구현
  - [ ] `SearchResult` 데이터클래스 구현

### 2.3 Port 인터페이스 구현
- [ ] `src/semantic_search/application/port/__init__.py` 생성
- [ ] `src/semantic_search/application/port/output/__init__.py` 생성
- [ ] `src/semantic_search/application/port/output/embedding_port.py` 생성
  - [ ] `EmbeddingPort` ABC 인터페이스 구현
  - [ ] `generate_embedding(text: str) -> List[float]` 추상 메서드 정의

### 2.4 Embedding Adapter 구현
- [ ] `src/semantic_search/adapter/__init__.py` 생성
- [ ] `src/semantic_search/adapter/output/__init__.py` 생성
- [ ] `src/semantic_search/adapter/output/embedding/__init__.py` 생성
- [ ] `src/semantic_search/adapter/output/embedding/sentence_transformer_adapter.py` 생성
  - [ ] `SentenceTransformerAdapter` 클래스 구현
  - [ ] 모델 지연 로딩 로직 구현 (`_load_model`)
  - [ ] `generate_embedding` 메서드 구현

### 2.5 Embedding Service 구현
- [ ] `src/semantic_search/application/service/__init__.py` 생성
- [ ] `src/semantic_search/application/service/embedding_service.py` 생성
  - [ ] `EmbeddingService` 클래스 구현
  - [ ] `create_embedding_for_document` 메서드 구현
  - [ ] `create_embedding_for_convention` 메서드 구현
  - [ ] `_create_document_text` 헬퍼 메서드 구현
  - [ ] `_create_convention_text` 헬퍼 메서드 구현

---

## Phase 3: Repository 확장

### 3.1 DomainDocumentRepository 확장
- [ ] `src/domain_document/adapter/output/persistence/repository.py` 수정
  - [ ] `update_embedding(document_id, embedding)` 메서드 추가
  - [ ] `semantic_search(query_embedding, top_k, similarity_threshold)` 메서드 추가
  - [ ] SQL 쿼리 작성 (pgvector cosine similarity)
  - [ ] 결과를 DomainDocument 객체로 변환하는 로직 구현

### 3.2 ProjectConventionRepository 확장
- [ ] `src/project_convention/adapter/output/persistence/repository.py` 수정
  - [ ] `update_embedding(convention_id, embedding)` 메서드 추가
  - [ ] `semantic_search(query_embedding, top_k, similarity_threshold)` 메서드 추가
  - [ ] SQL 쿼리 작성 (pgvector cosine similarity)
  - [ ] 결과를 ProjectConvention 객체로 변환하는 로직 구현

---

## Phase 4: Semantic Search Service 구현

- [ ] `src/semantic_search/application/service/semantic_search_service.py` 생성
  - [ ] `SemanticSearchService` 클래스 구현
  - [ ] `search(query, top_k, similarity_threshold)` 메서드 구현
    - [ ] 쿼리 임베딩 생성 로직
    - [ ] 도메인 문서 검색 로직
    - [ ] 컨벤션 검색 로직
    - [ ] 결과 병합 및 정렬 로직
  - [ ] `_document_to_dict` 헬퍼 메서드 구현
  - [ ] `_convention_to_dict` 헬퍼 메서드 구현

---

## Phase 5: 기존 서비스 통합

### 5.1 DocumentService 수정
- [ ] `src/domain_document/application/service/document_service.py` 수정
  - [ ] `__init__`에 `embedding_service` 파라미터 추가 (Optional)
  - [ ] `create_or_update_document` 메서드 수정
    - [ ] 문서 저장 후 임베딩 자동 생성 로직 추가
    - [ ] try-except로 임베딩 실패 처리 (로그만 기록)

### 5.2 ConventionService 수정
- [ ] `src/project_convention/application/service/convention_service.py` 수정
  - [ ] `__init__`에 `embedding_service` 파라미터 추가 (Optional)
  - [ ] `create_or_update_convention` 메서드 수정
    - [ ] 컨벤션 저장 후 임베딩 자동 생성 로직 추가
    - [ ] try-except로 임베딩 실패 처리 (로그만 기록)

---

## Phase 6: Container 설정

- [ ] `src/container.py` 수정
  - [ ] `SentenceTransformerAdapter` import 추가
  - [ ] `EmbeddingService` import 추가
  - [ ] `SemanticSearchService` import 추가
  - [ ] `embedding_adapter` Singleton provider 추가
  - [ ] `embedding_service` Factory provider 추가
  - [ ] `semantic_search_service` Factory provider 추가
  - [ ] `document_service`에 `embedding_service` 주입
  - [ ] `convention_service`에 `embedding_service` 주입

---

## Phase 7: MCP Handler 추가

### 7.1 Handler 함수 추가
- [ ] `src/mcp/handler.py` 수정
  - [ ] `semantic_search` 함수 구현
    - [ ] 파라미터: `query`, `top_k`, `similarity_threshold`
    - [ ] Container에서 `semantic_search_service` 가져오기
    - [ ] 검색 실행 및 결과 반환 (dict 형태)

### 7.2 MCP Server 등록
- [ ] `mcp_server.py` 수정
  - [ ] `@server.list_tools()`에 `semantic_search` 툴 정의 추가
    - [ ] name: "semantic_search"
    - [ ] description 작성
    - [ ] inputSchema 정의 (query, top_k, similarity_threshold)
  - [ ] `@server.call_tool()`에 `semantic_search` 핸들러 추가
    - [ ] 파라미터 파싱
    - [ ] `handler.semantic_search()` 호출
    - [ ] JSON 결과 반환

---

## Phase 8: 기존 데이터 마이그레이션

### 8.1 배치 스크립트 작성
- [ ] `scripts/generate_embeddings_batch.py` 생성
  - [ ] Container 설정
  - [ ] Repository 및 Service 가져오기
  - [ ] 모든 도메인 문서 조회 로직
  - [ ] 모든 컨벤션 조회 로직
  - [ ] 임베딩 생성 배치 처리 (tqdm 사용)
  - [ ] 에러 처리 및 로그 기록
  - [ ] 진행 상황 표시

### 8.2 배치 실행
- [ ] `poetry run python scripts/generate_embeddings_batch.py` 실행
- [ ] 실행 결과 확인
- [ ] DB에서 임베딩 생성 여부 확인 (`SELECT COUNT(*) FROM domain_document WHERE embedding IS NOT NULL`)

---

## 검증 및 테스트

### DB 검증
- [ ] pgvector 확장 설치 확인
- [ ] `domain_document` 테이블에 `embedding` 컬럼 존재 확인
- [ ] `project_convention` 테이블에 `embedding` 컬럼 존재 확인
- [ ] HNSW 인덱스 생성 확인

### 기능 테스트
- [ ] 새 도메인 문서 생성 시 임베딩 자동 생성 확인
- [ ] 새 컨벤션 생성 시 임베딩 자동 생성 확인
- [ ] `semantic_search` 함수 직접 호출 테스트
- [ ] MCP Tool을 통한 검색 테스트 (Claude Code에서)
- [ ] 유사도 점수가 올바르게 계산되는지 확인
- [ ] 여러 쿼리로 검색 결과 품질 확인

### 성능 테스트
- [ ] 임베딩 생성 시간 측정 (단일 문서)
- [ ] 검색 시간 측정 (다양한 top_k 값)
- [ ] 배치 처리 시간 측정 (전체 데이터)
- [ ] 메모리 사용량 확인

### 에러 처리 테스트
- [ ] 임베딩 생성 실패 시 문서 저장은 성공하는지 확인
- [ ] 잘못된 쿼리 입력 시 에러 처리 확인
- [ ] 빈 결과 반환 시 정상 동작 확인

---

## 문서화

- [ ] README에 RAG 기능 사용법 추가
- [ ] MCP Tool 문서 업데이트 (`semantic_search` 추가)
- [ ] API 문서 작성 (필요시)
- [ ] 예제 쿼리 및 결과 문서화

---

## 최종 점검

- [ ] 코드 리뷰
- [ ] 타입 힌트 확인
- [ ] 로깅 추가 (주요 작업에 대해)
- [ ] 불필요한 주석 제거
- [ ] 코드 포맷팅 (black, isort)
- [ ] Git commit 및 push

---

## 진행 상황

**시작일**: [날짜 입력]
**예상 완료일**: [시작일 + 6-7일]

**현재 Phase**: -
**완료된 Phase**: -

**이슈 및 블로커**:
- 없음

**참고 사항**:
- 각 작업 완료 시 체크박스에 체크 표시
- 이슈 발생 시 "이슈 및 블로커" 섹션에 기록
- Phase 완료 시 "완료된 Phase" 업데이트
