# Tool Service (Domain & Convention Management Agent)

## 프로젝트 개요

Tool Service (Domain & Convention Management Agent)는 소프트웨어 개발의 핵심 자산인 **도메인 지식**과 **프로젝트 컨벤션**을 독립된 모듈로 관리하고, AI Agent가 이를 적재적소에 참조하도록 돕는 시스템입니다.

이 프로젝트는 두 개의 독립적인 Bounded Context(`domain_document`와 `project_convention`)를 가지며, 각각 헥사고날 아키텍처로 구현되었습니다.

-   **`domain_document`**: 도메인 정의, 속성, 정책, 관계 등을 관리합니다. "우리가 무엇을 만드는가"에 대한 정보를 담습니다.
-   **`project_convention`**: 프로젝트별 표준 및 규칙을 관리합니다. "우리가 어떻게 만드는가"에 대한 정보를 담습니다.

## 설치 및 실행

### 1. 프로젝트 클론 및 의존성 설치

```bash
# git clone <repository_url>  # 프로젝트 클론
# cd <project_directory>      # 프로젝트 디렉토리로 이동
poetry install
```

### 2. 환경 변수 설정 (`.env`)

프로젝트 루트에 `.env` 파일을 생성하고 데이터베이스 연결 정보를 설정합니다.

```ini
# .env 파일 예시
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tool_service_db
```
`your_db_user`와 `your_db_password`는 실제 PostgreSQL 사용자명과 비밀번호로 변경해야 합니다.

### 3. 데이터베이스 초기화 (Seed Data)

애플리케이션을 시작하기 전에 필요한 초기 데이터를 데이터베이스에 주입해야 합니다.

```bash
# poetry run python seed.py
```
**참고**: `seed.py` 파일은 초기 데이터 주입 후 자동으로 삭제됩니다.

### 4. FastAPI 서버 실행

웹 어댑터가 올바르게 작동하는지 확인하려면 FastAPI 서버를 시작합니다.

```bash
poetry run uvicorn main:app --reload
```
서버가 시작되면 `http://localhost:8000/docs`에서 Swagger UI를 통해 API 문서를 확인할 수 있습니다.

## 테스트

### 웹 API 엔드포인트

*   **API 문서:** `http://localhost:8000/docs`
*   **프로젝트 컨벤션 조회 (예시):** `http://localhost:8000/conventions/Ttutta`

### AI Agent 시뮬레이션 (MCP Tool 핸들러)

`src/mcp/handler.py`에 정의된 `read_domain_spec`, `read_project_conventions`, `analyze_impact` 함수는 AI Agent (MCP)가 사용할 도구들입니다. Agent에게 다음과 같은 질문을 통해 도구 호출 및 동작을 검증할 수 있습니다:

> "User 도메인에 nickname 필드를 추가하는 마이그레이션 코드를 짜줘"

Agent의 응답을 통해 `read_domain_spec`과 `read_project_conventions`가 적절히 호출되는지 확인하십시오.
