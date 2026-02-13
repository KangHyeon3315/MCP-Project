# DCMA (Domain & Convention Management Agent) 설정 가이드

## 프로젝트 개요

DCMA는 도메인 문서와 프로젝트 컨벤션을 관리하는 MCP(Model Context Protocol) 서버입니다.
FastAPI 기반의 웹 UI와 API를 제공하며, AI 에이전트가 MCP 도구를 통해 도메인 명세와 컨벤션을 조회/관리할 수 있습니다.

---

## 1. 환경 설정

### 사전 요구사항

- Python 3.11+
- Poetry
- PostgreSQL 데이터베이스

### 의존성 설치

```bash
poetry install
```

### 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```ini
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
```

---

## 2. FastAPI 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 접속 URL

| URL | 설명 |
|-----|------|
| `http://localhost:8000` | 루트 (상태 확인) |
| `http://localhost:8000/ui/` | 웹 UI |
| `http://localhost:8000/docs` | Swagger API 문서 |
| `http://localhost:8000/redoc` | ReDoc API 문서 |

---

## 3. Docker 실행

### 이미지 빌드 및 실행

```bash
docker compose up -d --build
```

### 중지

```bash
docker compose down
```

`docker-compose.yml`에서 포트 및 DB 접속 정보를 수정할 수 있습니다.

---

## 4. MCP 도구 목록

`src/mcp/handler.py`에 정의된 MCP 도구들입니다.

### 조회 도구

#### `read_domain_spec` — 도메인 명세 조회

특정 도메인의 데이터 구조, 속성, 정책, 의존 관계를 조회합니다.

```json
{
  "project_name": "Ttutta",
  "service_name": "Auth",
  "domain_name": "User",
  "version": 1
}
```

- `version`은 선택 사항이며, 생략 시 최신 버전을 반환합니다.
- 반환: `DomainDocument` (properties, policies, dependencies 포함)

#### `read_project_conventions` — 프로젝트 컨벤션 조회

프로젝트의 스타일/아키텍처 규칙을 조회합니다.

```json
{
  "project_name": "Ttutta",
  "category": "NAMING"
}
```

- `category`는 선택 사항이며, 생략 시 전체 컨벤션을 반환합니다.
- 반환: `ProjectConvention` 리스트

#### `analyze_impact` — 도메인 영향도 분석

특정 도메인을 참조하는 다른 도메인들을 분석합니다.

```json
{
  "project_name": "Ttutta",
  "service_name": "Auth",
  "domain_name": "User"
}
```

- 반환: 영향도 분석 텍스트

### 생성/수정 도구

#### `create_or_update_domain_document` — 도메인 문서 생성/수정

새 도메인 문서를 생성하거나 기존 문서의 새 버전을 생성합니다.

```json
{
  "project_name": "Ttutta",
  "service_name": "Auth",
  "domain_name": "User",
  "summary": "사용자 계정 및 인증 정보를 관리하는 핵심 도메인",
  "properties": [
    {
      "name": "email",
      "type": "String",
      "description": "이메일",
      "is_required": true,
      "is_immutable": false
    }
  ],
  "policies": [
    {
      "category": "PERMISSION",
      "subject": "ADMIN",
      "content": "관리자만 접근 가능"
    }
  ]
}
```

- 반환: 생성/수정된 `DomainDocument`

#### `create_or_update_project_convention` — 프로젝트 컨벤션 생성/수정

새 컨벤션을 생성하거나 기존 컨벤션의 새 버전을 생성합니다.

```json
{
  "project_name": "Ttutta",
  "category": "NAMING",
  "title": "변수 명명 규칙",
  "content": "CamelCase를 사용한다.",
  "example_correct": "userName",
  "example_incorrect": "user_name"
}
```

- `example_correct`, `example_incorrect`는 선택 사항입니다.
- 반환: 생성/수정된 `ProjectConvention`

### 삭제 도구

#### `soft_delete_domain_document` — 도메인 문서 삭제

해당 도메인의 모든 버전을 소프트 삭제합니다.

```json
{
  "project_name": "Ttutta",
  "service_name": "Auth",
  "domain_name": "User"
}
```

#### `soft_delete_project_convention` — 프로젝트 컨벤션 삭제

해당 컨벤션의 모든 버전을 소프트 삭제합니다.

```json
{
  "project_name": "Ttutta",
  "category": "NAMING",
  "title": "변수 명명 규칙"
}
```

---

## 5. API 엔드포인트

### REST API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/conventions/{project_name}` | 프로젝트 컨벤션 목록 조회 |
| `GET` | `/domains/{project_name}/{service_name}/{domain_name}?version=1` | 도메인 명세 조회 |

### 웹 UI

| 경로 | 설명 |
|------|------|
| `/ui/` | 프로젝트 목록 |
| `/ui/projects/{project_name}` | 프로젝트 상세 (도메인 + 컨벤션) |
| `/ui/domains/{project_name}/{service_name}/{domain_name}` | 도메인 상세 (버전 히스토리) |
| `/ui/conventions/{project_name}/{category}/{title}` | 컨벤션 상세 (버전 히스토리) |

---

## 6. 프로젝트 구조

```
mcp/
├── main.py                     # FastAPI 앱 진입점
├── pyproject.toml              # 의존성 관리
├── docker-compose.yml          # Docker 설정
├── Dockerfile
├── .env                        # 환경 변수
├── templates/                  # Jinja2 HTML 템플릿
├── src/
│   ├── container.py            # DI 컨테이너
│   ├── mcp/
│   │   └── handler.py          # MCP 도구 핸들러
│   ├── web/
│   │   ├── router.py           # REST API 라우터
│   │   └── ui_router.py        # 웹 UI 라우터
│   ├── domain_document/        # 도메인 문서 바운디드 컨텍스트
│   │   ├── adapter/
│   │   ├── application/
│   │   └── domain/
│   └── project_convention/     # 프로젝트 컨벤션 바운디드 컨텍스트
│       ├── adapter/
│       ├── application/
│       └── domain/
└── tests/                      # 테스트
```
