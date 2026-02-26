# mcp-project - AI Agent 사용 가이드

## 1. 프로젝트 개요

이 MCP 서버는 소프트웨어 개발의 핵심 자산인 **도메인 지식**과 **프로젝트 컨벤션**을 중앙에서 관리하고, AI 에이전트가 코드 생성/수정 시 이를 참조하도록 돕는 시스템입니다.

**왜 필요한가?**
- **도메인 지식 중앙화**: 도메인 구조, 속성, 정책, 의존성을 문서화하여 일관된 코드 생성
- **프로젝트 규칙 준수**: 명명 규칙, 아키텍처 패턴, 테스트 전략을 자동으로 반영
- **안전한 변경**: 도메인 수정 전 영향도 분석으로 Side Effect 최소화
- **빠른 탐색**: 자연어 검색으로 관련 도메인/규칙 즉시 발견

**언제 사용하는가?**
- 🔧 **코드 작성 전**: 도메인 구조와 정책 확인 필수
- 🏗️ **도메인 설계 시**: 기존 개념과 충돌 여부 파악
- ✏️ **도메인 수정 전**: 영향 받는 다른 도메인 분석 필수
- 📋 **코드 리뷰 시**: 프로젝트 규칙 준수 여부 검증

---

## 2. 8개 MCP 도구 설명

### 조회 도구 (4개)

#### `read_domain_spec` ⭐ (필수)

**목적**: 도메인의 속성, 정책, 의존성 조회

**언제 사용**:
1. **도메인 설계 시**: 기존에 이미 있는 개념인지 파악
2. **코드 작성 전**: 도메인 구조 파악 필수
3. **영향도 분석 후**: 영향 받는 도메인의 상세 정보 확인

**입력**:
- `project_name` (필수): 프로젝트 이름 (예: "my-project")
- `service_name` (필수): 서비스 이름 (예: "Auth")
- `domain_name` (필수): 도메인 이름 (예: "User")
- `version` (선택): 버전 번호 (생략 시 최신)

**출력**: `DomainDocument` (properties, policies, dependencies 포함)

**예제**:
```json
read_domain_spec("my-project", "Auth", "User")

// 반환 예시:
{
  "project": "my-project",
  "service": "Auth",
  "domain": "User",
  "version": 1,
  "summary": "사용자 계정 및 인증 정보를 관리하는 핵심 도메인",
  "properties": [
    {
      "name": "email",
      "type": "String",
      "description": "사용자 이메일 주소",
      "is_required": true,
      "is_immutable": false
    },
    {
      "name": "password",
      "type": "String",
      "description": "암호화된 비밀번호",
      "is_required": true,
      "is_immutable": false
    }
  ],
  "policies": [
    {
      "category": "PERMISSION",
      "subject": "ADMIN",
      "content": "ADMIN 역할만 전체 사용자 목록 조회 가능"
    },
    {
      "category": "PERMISSION",
      "subject": "USER",
      "content": "일반 사용자는 본인의 정보만 조회 가능"
    }
  ]
}
```

---

#### `read_project_conventions`

**목적**: 프로젝트 코딩 규칙 조회

**언제 사용**:
- 특정 카테고리 규칙이 명확할 때 (semantic_search 후 사용 권장)
- 전체 규칙 목록을 한 번에 확인할 때

**입력**:
- `project_name` (필수): 프로젝트 이름
- `category` (선택): 카테고리 필터 (NAMING, ARCHITECTURE, TESTING, DOCUMENTATION, ERROR_HANDLING 등)

**출력**: `ProjectConvention` 리스트

**권장**: 먼저 `semantic_search`로 관련 컨벤션 찾기!

**예제**:
```json
read_project_conventions("my-project", category="NAMING")

// 반환 예시:
[
  {
    "project": "my-project",
    "category": "NAMING",
    "title": "변수 명명 규칙",
    "content": "CamelCase를 사용하며, 약어는 최소화한다.",
    "example_correct": "userName, isActive",
    "example_incorrect": "user_name, is_active"
  },
  {
    "project": "my-project",
    "category": "NAMING",
    "title": "RESTful URL 규칙",
    "content": "리소스는 복수형, kebab-case 사용",
    "example_correct": "/users/{id}, /order-items",
    "example_incorrect": "/user/{id}, /orderItems"
  }
]
```

---

#### `analyze_impact` ⭐ (필수)

**목적**: 도메인 변경 시 영향 받는 다른 도메인 파악

**언제 사용**:
1. **도메인 설계 시**: 필수적으로 영향 받는 도메인 파악
2. **도메인 수정 전**: 의존성 확인 필수
3. **리팩토링 전**: 변경 범위 파악

**입력**:
- `project_name` (필수): 프로젝트 이름
- `service_name` (필수): 서비스 이름
- `domain_name` (필수): 분석할 도메인 이름

**출력**: 영향도 분석 텍스트 (어떤 도메인들이 참조하는지)

**예제**:
```json
analyze_impact("my-project", "Auth", "User")

// 반환 예시:
"User 도메인은 Order, AuthLog 도메인에 의해 참조되고 있습니다."
```

**주의**: 도메인 설계/수정 시 **반드시** 사용! 영향 받는 코드를 함께 수정해야 합니다.

---

#### `semantic_search` 🔍 (우선 사용 권장)

**목적**: 자연어로 관련 도메인/규칙 검색

**언제 사용**:
1. **작업 시작 시**: `read_domain_spec`, `read_project_conventions` 대신 **먼저 사용**
2. **예시**: "조회 API 구현" → `semantic_search("조회 api 아키텍처")`
3. 정확한 이름 모를 때, 관련 항목 탐색 시
4. 도메인과 컨벤션을 동시에 검색할 때

**입력**:
- `query` (필수): 자연어 검색 쿼리 (한글/영어 모두 가능)
- `top_k` (선택, 기본 10): 반환할 최대 결과 수
- `similarity_threshold` (선택, 기본 0.3): 최소 유사도 점수 (0.0-1.0)

**출력**: 유사도 순으로 정렬된 문서 리스트 (도메인 + 컨벤션)

**예제**:
```json
// 좋은 예: 작업 시작 시
semantic_search("조회 api 아키텍처 컨벤션")

// 반환 예시:
{
  "query": "조회 api 아키텍처 컨벤션",
  "total_count": 5,
  "matches": [
    {
      "document_type": "PROJECT_CONVENTION",
      "document_id": "uuid-1",
      "similarity": 0.85,
      "content": {
        "category": "ARCHITECTURE",
        "title": "조회 API 아키텍처",
        "content": "헥사고날 아키텍처: Controller → UseCase → Repository"
      }
    },
    {
      "document_type": "PROJECT_CONVENTION",
      "document_id": "uuid-2",
      "similarity": 0.78,
      "content": {
        "category": "NAMING",
        "title": "API 엔드포인트 명명 규칙",
        "content": "GET /users, POST /users, GET /users/{id}"
      }
    },
    {
      "document_type": "DOMAIN_DOCUMENT",
      "document_id": "uuid-3",
      "similarity": 0.72,
      "content": {
        "domain": "User",
        "summary": "사용자 계정 관리",
        "properties": [...]
      }
    }
  ]
}

// 다른 예시: 인증 정책 검색
semantic_search("인증 정책 authentication policy")
// → User 도메인의 PERMISSION 정책 + 인증 관련 컨벤션 발견
```

**장점**:
- 도메인과 컨벤션을 한 번에 검색
- 정확한 이름 몰라도 됨
- 관련 항목을 유사도 순으로 제공

---

### 생성/수정 도구 (2개)

#### `create_or_update_domain_document`

**목적**: 도메인 문서 생성 또는 새 버전 생성

**언제 사용**:
- 신규 도메인 설계 후
- 기존 도메인 수정 후

**주의**: 항상 새 버전 생성 (기존 수정 안 함)

**입력**:
- `project_name` (필수): 프로젝트 이름
- `service_name` (필수): 서비스 이름
- `domain_name` (필수): 도메인 이름
- `summary` (필수): 도메인 요약 설명
- `properties` (필수): 속성 리스트
  - `name`: 속성 이름
  - `type`: 데이터 타입 (String, Integer, UUID, Enum 등)
  - `description`: 속성 설명
  - `is_required`: 필수 여부 (boolean)
  - `is_immutable`: 불변 여부 (boolean)
- `policies` (필수): 정책 리스트
  - `category`: 정책 카테고리 (PERMISSION, VALIDATION, BUSINESS_RULE 등)
  - `subject`: 정책 대상 (ADMIN, USER, SYSTEM 등)
  - `content`: 정책 내용

**출력**: 생성/수정된 `DomainDocument`

**예제**:
```json
create_or_update_domain_document(
    project_name="my-project",
    service_name="Auth",
    domain_name="User",
    summary="사용자 계정 및 인증 정보를 관리하는 핵심 도메인",
    properties=[
        {
            "name": "user_id",
            "type": "UUID",
            "description": "사용자 고유 식별자",
            "is_required": true,
            "is_immutable": true
        },
        {
            "name": "nickname",
            "type": "String",
            "description": "사용자 별명",
            "is_required": false,
            "is_immutable": false
        }
    ],
    policies=[
        {
            "category": "PERMISSION",
            "subject": "USER",
            "content": "일반 사용자는 본인 정보만 수정 가능"
        }
    ]
)
```

---

#### `create_or_update_project_convention`

**목적**: 프로젝트 규칙 생성 또는 새 버전 생성

**언제 사용**:
- 신규 규칙 정의 후
- 기존 규칙 수정 후

**입력**:
- `project_name` (필수): 프로젝트 이름
- `category` (필수): 카테고리 (NAMING, ARCHITECTURE, TESTING 등)
- `title` (필수): 규칙 제목
- `content` (필수): 규칙 내용
- `example_correct` (선택): 올바른 예시
- `example_incorrect` (선택): 잘못된 예시

**출력**: 생성/수정된 `ProjectConvention`

**예제**:
```json
create_or_update_project_convention(
    project_name="my-project",
    category="NAMING",
    title="변수 명명 규칙",
    content="CamelCase를 사용하며, 약어는 최소화한다.",
    example_correct="userName, isActive",
    example_incorrect="user_name, is_active"
)
```

---

### 삭제 도구 (2개)

#### `soft_delete_domain_document`

**목적**: 도메인의 모든 버전 소프트 삭제

**주의**: 복구 가능 (deleted_at 설정)

**입력**:
- `project_name` (필수): 프로젝트 이름
- `service_name` (필수): 서비스 이름
- `domain_name` (필수): 삭제할 도메인 이름

**출력**: "N records soft-deleted for domain 'User'."

---

#### `soft_delete_project_convention`

**목적**: 규칙의 모든 버전 소프트 삭제

**주의**: 복구 가능 (deleted_at 설정)

**입력**:
- `project_name` (필수): 프로젝트 이름
- `category` (필수): 카테고리
- `title` (필수): 삭제할 규칙 제목

**출력**: "N records soft-deleted for convention '변수 명명 규칙'."

---

## 3. 필수 워크플로우

### Workflow 1: 새 API 엔드포인트 생성 (semantic_search 먼저!)

**사용자 요청**: "User 도메인 조회 API 만들어줘"

**단계**:

```
1. semantic_search("조회 api 아키텍처 컨벤션")
   → 조회 API 아키텍처 컨벤션, 네이밍 컨벤션(common) 등 발견

2. read_domain_spec("my-project", "Auth", "User")
   → properties: id, email, password, created_at
   → policies: ADMIN만 전체, 본인만 자기 정보

3. (필요 시) 추가 컨벤션 조회:
   read_project_conventions("my-project", category="ARCHITECTURE")
   → 헥사고날 아키텍처, Service → Repository

4. 코드 생성:
   - domain_spec 기반 DTO
   - policies 기반 권한 체크
   - conventions 준수 구조
```

**핵심**: `semantic_search`를 **먼저** 사용하여 관련 도메인과 컨벤션을 한 번에 발견!

---

### Workflow 2: 도메인 필드 추가 (영향도 분석 필수!)

**사용자 요청**: "User에 nickname 추가하고 마이그레이션 작성"

**단계**:

```
1. read_domain_spec("my-project", "Auth", "User")
   → 현재 속성 확인

2. analyze_impact("my-project", "Auth", "User") ⭐ 필수
   → "User는 Order, AuthLog에 의해 참조됩니다"

3. read_domain_spec("my-project", "Order", "Order")
   → user_id만 사용 → nickname 영향 없음 확인

4. semantic_search("마이그레이션 데이터베이스 컨벤션")
   → DB 마이그레이션 규칙 확인

5. create_or_update_domain_document(...)
   → nickname 속성 추가한 새 버전 생성

6. 마이그레이션 코드 생성:
   - ALTER TABLE users ADD COLUMN nickname VARCHAR(50)
```

**핵심**: `analyze_impact`를 **반드시** 사용하여 영향 받는 도메인 파악!

---

### Workflow 3: 코드 리뷰 (semantic_search로 관련 규칙 찾기)

**사용자 요청**: "이 User Service 코드가 규칙을 준수하는지 확인"

**단계**:

```
1. semantic_search("서비스 레이어 아키텍처 네이밍 규칙")
   → 관련 컨벤션 발견

2. 코드 분석:
   - NAMING 규칙 검증
   - ARCHITECTURE 패턴 검증
   - TESTING 규칙 검증

3. 관련 도메인 확인:
   read_domain_spec("my-project", "Auth", "User")
   → 속성 타입 검증, 정책 준수 확인

4. 리뷰 코멘트 작성
```

**핵심**: `semantic_search`로 관련 규칙을 먼저 찾고, 세부 확인은 `read_*` 도구 사용!

---

## 4. 도구 선택 가이드

### 의사결정 트리 (semantic_search 우선!)

```
무엇을 하려는가?

├─ 정보 조회 → 🔍 먼저 semantic_search 사용 (권장!)
│  │
│  ├─ 작업 시작 시:
│  │  1. semantic_search("작업 관련 키워드")  ← 먼저!
│  │  2. 발견된 도메인/컨벤션 상세 조회
│  │     ├─ read_domain_spec (도메인 상세)
│  │     └─ read_project_conventions (컨벤션 상세)
│  │
│  ├─ 예시:
│  │  "조회 API 구현" → semantic_search("조회 api 아키텍처")
│  │  "User 도메인" → semantic_search("user 사용자") → read_domain_spec
│  │
│  └─ 정확한 이름 알 때만 직접 조회
│
├─ 도메인 설계/수정 → analyze_impact 필수! ⭐
│  1. semantic_search로 유사 도메인 탐색
│  2. read_domain_spec으로 현재 상태 확인
│  3. analyze_impact로 영향 받는 도메인 파악
│  4. create_or_update_domain_document
│
├─ 생성/수정
│  ├─ 도메인 → create_or_update_domain_document
│  └─ 규칙 → create_or_update_project_convention
│
└─ 삭제
   ├─ 도메인 → soft_delete_domain_document
   └─ 규칙 → soft_delete_project_convention
```

---

### FAQ

**Q: 작업 시작 시 어떤 도구부터?**

→ **semantic_search 먼저!** (권장)
- 예: "조회 API 구현" → `semantic_search("조회 api 아키텍처 컨벤션")`
- 관련 도메인과 컨벤션을 한 번에 발견
- 그 다음 `read_domain_spec`으로 상세 조회

**Q: semantic_search vs read_domain_spec vs read_project_conventions?**

1. **semantic_search**: 작업 시작 시 먼저 사용 (우선 순위 1)
   - 정확한 이름 몰라도 됨
   - 도메인 + 컨벤션 동시 검색
   - 유사도 순으로 정렬

2. **read_domain_spec**: semantic_search 결과에서 도메인 발견 후 상세 조회
   - 정확한 이름 알 때
   - 도메인만 조회

3. **read_project_conventions**: 특정 카테고리가 명확할 때만
   - 전체 규칙 조회 시
   - 카테고리 필터링 시

**Q: analyze_impact는 언제 필수?**

→ 도메인 설계/수정 시 **반드시** 사용! ⭐
- 신규 도메인 설계: 유사 도메인과 충돌 확인
- 기존 도메인 수정: 영향 받는 다른 도메인 파악

**Q: version 매개변수는 언제?**

- 생략: 최신 버전 (대부분의 경우)
- 지정: 특정 시점 상태, 버전 비교

**Q: category는 언제?**

- 생략: 전체 규칙 (초기 파악)
- 지정: 특정 영역만 (NAMING, TESTING 등)
- **권장**: semantic_search 먼저 사용

---

## 5. 베스트 프랙티스

### DO (권장)

✅ **작업 시작 시 semantic_search 먼저** 🔍
  - 예: `semantic_search("조회 api 컨벤션")`
  - 관련 도메인과 규칙을 한 번에 발견

✅ **도메인 설계/수정 시 analyze_impact 필수** ⭐
  - 도메인 간 의존성 파악
  - 영향 받는 코드 함께 수정

✅ **코드 작성 전 항상 도메인 조회**
  - `semantic_search` → `read_domain_spec`
  - 도메인 구조와 정책 확인

✅ **규칙 준수 검증**
  - `semantic_search`로 관련 컨벤션 찾기
  - 명명 규칙, 아키텍처 패턴 확인

✅ **권장 워크플로우**
  - `semantic_search` → `read_domain_spec` → `analyze_impact` → 생성

---

### DON'T (금지)

❌ **조회 없이 코드 생성**
  - 도메인 구조 확인 필수

❌ **영향도 분석 생략**
  - 도메인 수정 시 `analyze_impact` 필수

❌ **하드코딩된 도메인 구조**
  - 항상 `read_domain_spec` 결과 사용

❌ **컨벤션 무시**
  - `semantic_search`로 관련 규칙 찾기

❌ **정확한 이름 없이 read_* 직접 호출**
  - 먼저 `semantic_search`로 탐색

---

## 6. 실전 예제

### 예제 1: 신규 도메인 설계 (semantic_search + analyze_impact)

**사용자**: "Payment 도메인 설계하고 문서화"

**단계**:

```
1. semantic_search("결제 payment transaction")
   → 유사한 Order 도메인 발견

2. read_domain_spec("my-project", "Order", "Order")
   → amount, status 패턴 참고

3. semantic_search("도메인 설계 규칙")
   → 도메인 설계 컨벤션 발견

4. analyze_impact("my-project", "Payment", "Payment") ⭐
   → 신규 도메인이지만 Order와 관계 확인

5. create_or_update_domain_document(
      project_name="my-project",
      service_name="Payment",
      domain_name="Payment",
      summary="결제 처리 및 트랜잭션 관리",
      properties=[
          {
              "name": "payment_id",
              "type": "UUID",
              "description": "결제 고유 식별자",
              "is_required": true,
              "is_immutable": true
          },
          {
              "name": "order_id",
              "type": "UUID",
              "description": "주문 ID",
              "is_required": true,
              "is_immutable": true
          },
          {
              "name": "amount",
              "type": "Decimal",
              "description": "결제 금액",
              "is_required": true,
              "is_immutable": false
          },
          {
              "name": "status",
              "type": "Enum[PENDING, COMPLETED, FAILED]",
              "description": "결제 상태",
              "is_required": true,
              "is_immutable": false
          }
      ],
      policies=[
          {
              "category": "PERMISSION",
              "subject": "USER",
              "content": "사용자는 본인의 결제만 조회 가능"
          },
          {
              "category": "BUSINESS_RULE",
              "subject": "SYSTEM",
              "content": "결제 완료 후에는 금액 수정 불가"
          }
      ]
  )
```

---

### 예제 2: 탐색적 검색 (semantic_search 활용)

**사용자**: "인증 관련 정책 모두 찾아줘"

**단계**:

```
1. semantic_search("인증 authentication 정책 policy", top_k=10) 🔍
   → User, AuthLog 도메인 + 인증 관련 컨벤션 발견

   // 반환 예시:
   {
     "matches": [
       {
         "document_type": "DOMAIN_DOCUMENT",
         "domain": "User",
         "similarity": 0.89
       },
       {
         "document_type": "DOMAIN_DOCUMENT",
         "domain": "AuthLog",
         "similarity": 0.82
       },
       {
         "document_type": "PROJECT_CONVENTION",
         "category": "ARCHITECTURE",
         "title": "세션 관리 규칙",
         "similarity": 0.76
       }
     ]
   }

2. read_domain_spec("my-project", "Auth", "User")
   → policies 확인: ADMIN만 전체 조회

3. read_domain_spec("my-project", "Auth", "AuthLog")
   → policies 확인: 로그인 시도 제한

4. 결과 정리 및 제시:
   - User 도메인: PERMISSION 정책 (ADMIN만 전체 조회)
   - AuthLog 도메인: VALIDATION 정책 (로그인 시도 제한)
   - 인증 관련 컨벤션: 세션 관리 규칙
```

---

## 7. 트러블슈팅

### "도메인을 찾을 수 없습니다"

**원인**: 잘못된 이름 또는 존재하지 않는 도메인

**해결**:
1. `semantic_search`로 먼저 탐색
   ```
   semantic_search("user 사용자")
   ```
2. `project_name`, `service_name`, `domain_name` 철자 확인
3. 대소문자 구분 확인

---

### "버전이 여러 개 있는데?"

**원인**: 도메인의 여러 버전 존재

**해결**:
- `version` 생략 시 최신 버전 자동 선택
- 특정 버전 필요 시:
  ```
  read_domain_spec("my-project", "Auth", "User", version=1)
  ```

---

### "검색 결과가 없습니다"

**원인**: 너무 구체적인 쿼리 또는 높은 threshold

**해결**:
1. 쿼리를 더 일반적으로 변경
   ```
   # 너무 구체적: "사용자 이메일 중복 검증 로직"
   # 일반적: "사용자 검증"
   semantic_search("사용자 검증")
   ```
2. `similarity_threshold` 낮추기
   ```
   semantic_search("query", similarity_threshold=0.2)
   ```
3. `top_k` 늘리기
   ```
   semantic_search("query", top_k=20)
   ```

---

### "영향도 분석 결과가 비어있습니다"

**원인**: 아직 다른 도메인이 참조하지 않음

**해결**:
- 신규 도메인인 경우 정상
- 참조 관계가 추가되면 자동으로 업데이트됨

---

## 8. 요약

### 핵심 원칙

1. **작업 시작 시 semantic_search 먼저** 🔍
   - 관련 도메인과 컨벤션을 한 번에 발견
   - 정확한 이름 몰라도 됨

2. **도메인 설계/수정 시 analyze_impact 필수** ⭐
   - 영향 받는 도메인 파악
   - 의존성 확인

3. **코드 작성 전 항상 도메인 조회**
   - 도메인 구조와 정책 확인
   - 일관된 코드 생성

4. **권장 워크플로우**
   ```
   semantic_search → read_domain_spec → analyze_impact → 생성
   ```

### 도구 우선 순위

1. **semantic_search**: 작업 시작 시 우선 사용
2. **read_domain_spec**: 도메인 상세 조회
3. **analyze_impact**: 도메인 설계/수정 시 필수
4. **create_or_update_***: 생성/수정 시

### 금지 사항

❌ 조회 없이 코드 생성
❌ 영향도 분석 생략
❌ 하드코딩된 도메인 구조
❌ 컨벤션 무시

---

**이 가이드를 따르면 AI 에이전트가 도메인 지식과 프로젝트 규칙을 올바르게 참조하여 정확하고 일관된 코드를 생성할 수 있습니다.**
