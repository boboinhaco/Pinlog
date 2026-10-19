# Pinlog (핀로그) — SNS 링크를 확인된 일정·장소·물품으로

SNS에서 발견한 정보를 AI가 **공식 출처와 대조해 확인**하고, 캘린더·지도·저장함으로 정리해주는 Personal Action Agent.
원티드 AI 챔피언십 2026 출품작 · 명세서 v3.0 기준.

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Pinia](https://img.shields.io/badge/Pinia-store-FFD859)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-asyncpg-4169E1?logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

| | |
|---|---|
| **형태** | 개인 프로젝트 (원티드 AI 챔피언십 2026 출품, 2026.09) · 기획부터 배포까지 혼자 진행 |
| **내 역할** | 전체 · 기획/명세 → Vue 프론트(11개 뷰, Leaflet 지도, PWA) → FastAPI 백엔드와 DB 설계 → AI 파이프라인 5단계(이해·추출·정규화·출처 검색·검증)와 신뢰등급 설계 → 골든셋 평가 → Docker/Render 배포 |
| **문제** | SNS 게시물의 일정·장소·물품 정보는 틀리거나 오래된 경우가 많고, LLM에 그냥 물으면 근거 없이 확신함 |
| **해결** | 링크 → 이해 → 추출 → 정규화 → 공식 출처 검색 → 검증의 5단계 파이프라인. 숫자 confidence 대신 **HIGH / REVIEW / UNVERIFIED** 3등급과 필드별 상태로 "무엇이 확인됐는지"를 보여줌 |
| **기술 포인트** | BackgroundTask + SSE로 단계별 진행 스트리밍 · 정부·공공·금융 도메인 우선 정렬한 출처 검색 · 무료 등급 한도에 걸리면 자동 전환되는 LLM 폴백 체인 · 골든셋 기반 평가 스크립트 · 프론트와 API를 한 컨테이너로 묶어 CORS 없는 Render 배포 |

<p align="center"><img src="docs/screenshots/landing.jpg" width="900" alt="Pinlog 랜딩 화면"></p>

## 화면

랜딩(Hero → 문제 → 해결 → 신뢰 → 프로세스 → FAQ → 로그인) · 홈(링크 입력·추출된 일정·저장된 장소·월간 일정표) ·
내 일정 · 저장한 장소(지도/위성·필터, Leaflet) · 좋아요한 콘텐츠(AI 요약) · 링크 분석 결과(원본 게시물 ↔ 공식 공고 비교).

## 핵심 흐름

```
POST /api/shares (링크)
  → job QUEUED → BackgroundTask가 pipeline 실행: understand → extract → normalize → search → verify
      (단계별 결과를 DB에 저장)
  → GET /api/jobs/{id}/stream (SSE)  또는 2초 polling
  → GET /api/shares/{id}/result (원본 게시물 + 추출 + 검증)
  → 사용자가 확인 후 POST /api/shares/{id}/items → 캘린더 이벤트 · 장소 · 물품 저장
```

- 링크는 OG 태그·본문을 읽고, 인스타그램은 캡션과 첫 이미지를 사용합니다.
- 공식 출처는 웹 검색(Tavily) 후 정부·공공기관·금융기관 도메인을 우선 정렬해 상위 3건만 씁니다.
- 게시물에 대조할 구체적 사실이 없으면 비슷한 출처와 억지로 연결하지 않고 `UNVERIFIED`로 둡니다.
- 물건 소개 게시물(`PRODUCT`)은 사진 속 로고·글자·형태로 제품 후보를 뽑고, 웹 검색으로 상품명을 확인해 공식·구매처·네이버쇼핑 링크를 붙입니다. 브랜드·모델이 글자로 확인되면 "확실함", 생김새만 비슷하면 "비슷한 제품일 수 있음"으로 표시합니다.

## 신뢰등급

숫자 confidence 없음. **HIGH / REVIEW / UNVERIFIED** 3단계 + 필드별 상태(`VERIFIED` / `REFINED` / `CONFLICT` / `ADDED` / `AMBIGUOUS` / `UNVERIFIED`).
사용자는 어떤 필드가 공식 출처로 확인됐고 어떤 필드가 게시물 주장 그대로인지 구분해서 볼 수 있습니다.

## 구조

```
Pinlog/
├── frontend/   Vue 3 + Vite + Pinia + vue-router + Leaflet (PWA)
│   └── src/views/  Landing · Home · Calendar · Map · Liked · Analyze · ItemList · ItemDetail · Upload · Review · Category
├── backend/    FastAPI 단일 백엔드 — API + AI 파이프라인 + DB
│   ├── app/api/        라우터 (auth, shares, jobs, items, calendar, places)
│   ├── app/pipeline/   understand → extract → normalize → search → verify (+ products)
│   ├── app/services/   job 실행, SSE, LLM 호출(폴백 포함), 등급 산정
│   ├── app/db/         SQLAlchemy(asyncpg) 모델 + 세션
│   ├── db/migrations/  스키마 변경 SQL
│   ├── fixtures/demo/  예시 링크용 데모 데이터 (DEMO_MODE)
│   └── eval/golden/    골든셋 + 평가 스크립트
├── docs/       명세서
├── Dockerfile  프론트 빌드 + API 한 이미지
└── docker-compose.yml  web:5173 / api:8000 / db:5432
```

## 빠른 시작

```bash
cp .env.example .env          # LLM_API_KEY(Gemini), WEB_SEARCH_API_KEY(Tavily) 채우기
docker compose up --build     # web:5173 / api:8000 / db:5432
```

개별 실행

```bash
cd backend  && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --reload
cd frontend && npm i && npm run dev
```

스키마는 서버가 시작할 때 자동으로 준비합니다(테이블이 없으면 `backend/db/init.sql`, 그다음 `backend/db/migrations/*.sql`). `DEMO_MODE=true`면 API 키 없이 예시 링크로 화면을 볼 수 있습니다.

## 환경 변수

| 이름 | 설명 |
|---|---|
| `LLM_API_KEY` / `LLM_MODEL` | Gemini API 키 · 모델 (예: `gemini-3.6-flash`) |
| `LLM_FALLBACK_MODELS` | 일일 한도·장애 시 순서대로 대신 쓸 모델 (기본 `gemini-3.5-flash-lite,gemini-flash-latest`). 무료 등급은 모델별 하루 요청 수가 작아 한도에 닿으면 자동으로 다음 모델로 넘어갑니다 |
| `WEB_SEARCH_API_KEY` | 공식 출처 검색용 Tavily 키 |
| `KAKAO_REST_API_KEY` · `PUBLIC_DATA_API_KEY` | 장소 좌표 · 공공데이터 조회 (선택) |
| `DEMO_MODE` | `true`면 예시 링크(`PINLOG_SAMPLE_*`)를 데모 데이터로 응답 |
| `JWT_SECRET` | 로그인 세션 토큰 서명 키 |
| `DATABASE_URL` · `STORAGE_DIR` · `CORS_ORIGINS` | DB 접속 문자열 · 업로드 저장 경로 · 허용 origin |

## 배포 (Render)

루트의 `render.yaml`이 웹 서비스 하나(도커: 프론트 빌드 + API)와 Postgres를 정의합니다. 프론트와 API가 같은 주소에서 제공되어 CORS·프록시 설정이 필요 없습니다.

1. GitHub에 푸시된 상태에서 [Render](https://render.com) 가입 → **New → Blueprint** → 이 저장소 선택.
2. `LLM_API_KEY`와 `WEB_SEARCH_API_KEY`를 입력 → **Apply**. 첫 빌드 5~10분, `/health`가 `{"ok":true}`면 정상.

알아둘 점: 무료 웹 서비스는 15분 유휴 후 잠들어 첫 접속이 30~60초 걸립니다. 무료 Postgres는 30일 뒤 만료되므로 계속 쓰려면 [Neon](https://neon.tech) 같은 외부 Postgres URL을 `DATABASE_URL`에 넣습니다. 업로드한 스크린샷은 컨테이너 디스크에 저장되어 재배포하면 사라집니다(분석 결과는 DB에 남습니다).

배포 이미지를 로컬에서 미리 확인하려면

```bash
docker build -t pinlog .
docker run --rm -p 8000:8000 --env-file backend/.env -e DATABASE_URL=postgres://user:pass@host.docker.internal:5433/nexto pinlog
```

## 브랜치

`main`(데모 가능) ← `dev` ← `feat/fe-*`, `feat/be-*`, `feat/ai-*` (혼자 작업하지만 영역별로 브랜치를 나눠 관리)
