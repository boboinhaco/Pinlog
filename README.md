# Pinlog (핀로그) — SNS 링크를 확인된 다음 일정으로

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
이미 DB를 쓰고 있다면 스키마 변경을 한 번 적용해 주세요.
```bash
docker compose exec -T db psql -U nexto -d nexto < backend/db/migrations/002_user_profile.sql
```

## 환경 변수
| 이름 | 설명 |
|---|---|
| `LLM_API_KEY` / `LLM_MODEL` | Gemini API 키 · 모델 (예: `gemini-3.6-flash`) |
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

## 신뢰등급
숫자 confidence 없음. HIGH / REVIEW / UNVERIFIED 3단계 + 필드별 상태(VERIFIED/REFINED/CONFLICT/ADDED/AMBIGUOUS/UNVERIFIED).

## 화면
랜딩(Hero → 문제 → 해결 → 신뢰 → 프로세스 → FAQ → 로그인) · 홈(링크 입력·추출된 일정·저장된 장소·월간 일정표) ·
내 일정 · 저장한 장소(지도/위성·필터) · 좋아요한 콘텐츠(AI 요약) · 링크 분석 결과(원본 게시물 ↔ 공식 공고 비교).

## 브랜치
`main`(데모 가능) ← `dev` ← `feat/fe-*`, `feat/be-*`, `feat/ai-*`
