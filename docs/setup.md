# 개발 환경 설정 가이드

파트 A(프론트엔드) · B(AI) · C(백엔드) 각각의 로컬 실행 방법.  
Azure 리소스(Functions, Container Apps, SQL 등)는 별도로 프로비저닝 필요 → [`Azure_services.md`](Azure_services.md) 참조.

---

## 공통 필수 도구

| 도구 | 버전 | 설명 |
|---|---|---|
| Node.js | 18 이상 | 프론트엔드 실행 |
| Python | 3.11 | 백엔드·AI 실행 |
| uv | 최신 | Python 가상환경 + 패키지 관리 |
| Azure Functions Core Tools | v4 | 백엔드 로컬 실행 (`func start`) |
| ODBC Driver 18 for SQL Server | 18 | 백엔드 Azure SQL 연결 |

### Windows

```powershell
winget install OpenJS.NodeJS
winget install astral-sh.uv
winget install Microsoft.AzureFunctionsCoreTools
winget install Microsoft.msodbcsql.18
```

### macOS

```bash
brew install node
curl -LsSf https://astral.sh/uv/install.sh | sh
brew tap azure/functions && brew install azure-functions-core-tools@4
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

> 설치 후 터미널을 재시작해야 `func` 명령이 인식됨.

---

## 파트 A — 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 접속.  
백엔드 연동 전에는 API 호출이 실패하므로, 파트 C 로컬 서버를 함께 띄워야 정상 동작.

---

## 파트 B — AI 서비스

```bash
cd ai
uv venv --python 3.11
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

환경변수 설정 — `.env` 파일을 `ai/` 디렉토리에 생성:

```
AZURE_LANGUAGE_ENDPOINT=<Azure AI Language 엔드포인트>
AZURE_LANGUAGE_KEY=<Azure AI Language API 키>
GOOGLE_SAFE_BROWSING_API_KEY=<Google Safe Browsing API 키>
```

> 두 키 모두 없어도 서버는 실행됨. 해당 기능만 비활성화(`"enabled": false`)되고 모델 추론은 정상 동작.

로컬 실행:

```bash
uvicorn app.main:app --reload --port 8000
```

`http://localhost:8000` 접속 시 `{"message": "AI service is running"}` 응답 확인.  
최초 실행 시 HuggingFace에서 모델을 자동 다운로드하므로 시간이 걸릴 수 있음.

---

## 파트 C — 백엔드

```bash
cd backend
uv venv --python 3.11
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

환경변수 설정 — `local.settings.json.example`을 복사해 `local.settings.json` 생성 후 각 값을 채움:

```bash
cp local.settings.json.example local.settings.json
```

| 키 | 설명 |
|---|---|
| `AZURE_VISION_ENDPOINT` | Azure Vision 리소스 → 키 및 엔드포인트 |
| `AZURE_VISION_KEY` | 동일 |
| `BLOB_CONNECTION_STRING` | 스토리지 계정 → 액세스 키 → 연결 문자열 |
| `BLOB_CONTAINER_NAME` | 컨테이너 이름 (기본값: `images`) |
| `SQL_CONNECTION_STRING` | SQL Database → 연결 문자열 → ODBC |
| `CONTAINER_APP_URL` | 파트 B Container App 배포 후 입력 |

> `local.settings.json`은 `.gitignore`에 포함되어 커밋되지 않음.

로컬 실행:

```bash
func start
```

정상 실행 시:

```
Functions:
    analyze: [POST] http://localhost:7071/api/analyze
    history: [GET]  http://localhost:7071/api/history
```

---

## 동작 확인

파트 B(`localhost:8000`)와 파트 C(`localhost:7071`)를 모두 띄운 상태에서 테스트.  
API 명세는 [`api-contract.md`](api-contract.md) 참조.

**텍스트 분석:**

```bash
curl -X POST http://localhost:7071/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "고객님 계좌가 정지되었습니다. 아래 링크를 눌러 인증하세요."}'
```

**이미지 분석:**

```bash
curl -X POST http://localhost:7071/api/analyze \
  -F "file=@/path/to/image.jpg"
```

**이력 조회:**

```bash
curl "http://localhost:7071/api/history?limit=10&offset=0"
```
