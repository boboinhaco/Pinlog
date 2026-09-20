# Pinlog (핀로그) — SNS 링크를 확인된 일정·장소·물품으로

SNS에서 발견한 정보를 AI가 공식 출처와 대조해 확인하고, 캘린더·지도·저장함으로 정리해주는 Personal Action Agent.
원티드 AI 챔피언십 2026 · 명세서 v3.0 기준.

## 구조
```
Pinlog/
├── frontend/   Vue 3 + Vite + Pinia (랜딩 / 홈 / 내 일정 / 저장한 장소 / 좋아요한 콘텐츠 / 링크 분석 결과)
├── backend/    FastAPI 단일 백엔드 — API + AI 파이프라인 + DB
│   ├── app/api/        라우터 (auth, shares, jobs, items, calendar, places)
│   ├── app/pipeline/   understand → extract → normalize → search → verify
│   ├── app/services/   job 실행, SSE, LLM 호출, 등급 산정
│   ├── app/db/         SQLAlchemy 모델 + 세션
│   ├── db/migrations/  스키마 변경 SQL
│   ├── fixtures/demo/  예시 링크용 데모 데이터
│   └── eval/golden/    골든셋 + 평가 스크립트
├── docs/       명세서
└── docker-compose.yml
```

## 빠른 시작
```bash
cp .env.example .env          # LLM_API_KEY, WEB_SEARCH_API_KEY 채우기
docker compose up --build     # web:5173 / api:8000 / db:5432
```
개별 실행
```bash
cd backend  && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --reload
cd frontend && npm i && npm run dev
```
스키마는 서버가 시작할 때 자동으로 준비합니다(테이블이 없으면 `backend/db/init.sql`, 그다음 `backend/db/migrations/*.sql`).

## 배포 (Render)
루트의 `render.yaml`이 웹 서비스 하나(도커: 프론트 빌드 + API)와 Postgres를 정의합니다. 프론트와 API가 같은 주소에서 제공되어 CORS·프록시 설정이 필요 없습니다.

1. GitHub에 푸시된 상태에서 [Render](https://render.com) 가입 → **New → Blueprint** → 이 저장소 선택.
2. `render.yaml`을 읽어 서비스·DB를 만들고, `LLM_API_KEY`(Gemini)와 `WEB_SEARCH_API_KEY`(Tavily)를 물어보면 입력 → **Apply**.
3. 첫 빌드는 5~10분. 끝나면 `https://pinlog-xxxx.onrender.com` 형태의 주소가 생기고, `/health`가 `{"ok":true}`를 주면 정상입니다.

알아둘 점
- 무료 웹 서비스는 15분 동안 접속이 없으면 잠들어 첫 접속이 30~60초 걸립니다.
- 무료 Postgres는 생성 30일 뒤 만료됩니다. 계속 쓰려면 DB를 유료로 바꾸거나, [Neon](https://neon.tech) 같은 무료 Postgres의 접속 URL을 `DATABASE_URL`에 넣으면 됩니다(`?sslmode=require` 형식 그대로 사용 가능).
- 올린 스크린샷은 컨테이너 디스크에 저장되어 재배포하면 사라집니다(분석 결과는 DB에 남습니다).

배포 이미지를 로컬에서 미리 확인하려면
```bash
docker build -t pinlog .
docker run --rm -p 8000:8000 --env-file backend/.env -e DATABASE_URL=postgres://user:pass@host.docker.internal:5433/nexto pinlog
```

## 환경 변수
| 이름 | 설명 |
|---|---|
| `LLM_API_KEY` / `LLM_MODEL` | Gemini API 키 · 모델 (예: `gemini-3.6-flash`) |
| `LLM_FALLBACK_MODELS` | 일일 한도·장애 시 순서대로 대신 쓸 모델 (기본 `gemini-3.5-flash-lite,gemini-flash-latest`). 무료 등급은 모델별 하루 요청 수가 작아서(예: 20회) 한도에 닿으면 자동으로 다음 모델로 넘어가요 |
| `WEB_SEARCH_API_KEY` | 공식 출처 검색용 Tavily 키 |
| `DEMO_MODE` | `true`면 예시 링크(`PINLOG_SAMPLE_*`)를 데모 데이터로 응답 |
| `JWT_SECRET` | 로그인 세션 토큰 서명 키 |

## 핵심 흐름
`POST /api/shares`(링크) → job QUEUED → BackgroundTask가 단계 실행(단계별 결과를 DB 저장) →
`GET /api/jobs/{id}/stream`(SSE) 또는 2초 polling → `GET /api/shares/{id}/result`(원본 게시물 + 추출 + 검증) →
사용자가 확인 후 `POST /api/shares/{id}/items` → 캘린더 이벤트 생성.

- 링크는 OG 태그·본문을 읽고, 인스타그램은 캡션과 첫 이미지를 사용합니다.
- 공식 출처는 웹 검색 후 정부·공공기관·금융기관 도메인을 우선 정렬해 상위 3건만 씁니다.
- 게시물에 대조할 구체적 사실이 없으면 비슷한 출처와 연결하지 않고 `UNVERIFIED`로 둡니다.
- 물건을 소개하는 게시물(`PRODUCT`)은 사진 속 로고·글자·형태로 제품 후보를 뽑고, 웹 검색으로 상품명을 확인해 공식·구매처·네이버쇼핑 검색 링크를 붙입니다. 브랜드·모델이 글자로 확인되면 "확실함", 생김새만 비슷하면 "비슷한 제품일 수 있음"으로 표시하고, 구매 전 직접 확인하라는 안내를 함께 보여줍니다.

## 신뢰등급
숫자 confidence 없음. HIGH / REVIEW / UNVERIFIED 3단계 + 필드별 상태(VERIFIED/REFINED/CONFLICT/ADDED/AMBIGUOUS/UNVERIFIED).

## 화면
랜딩(Hero → 문제 → 해결 → 신뢰 → 프로세스 → FAQ → 로그인) · 홈(링크 입력·추출된 일정·저장된 장소·월간 일정표) ·
내 일정 · 저장한 장소(지도/위성·필터) · 좋아요한 콘텐츠(AI 요약) · 링크 분석 결과(원본 게시물 ↔ 공식 공고 비교).

## 브랜치
`main`(데모 가능) ← `dev` ← `feat/fe-*`, `feat/be-*`, `feat/ai-*`
