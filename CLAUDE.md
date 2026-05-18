# CLAUDE.md — AI 업무지침서

이 파일은 AI 에이전트가 프로젝트를 올바르게 이해하고 작업하기 위한 최우선 컨텍스트 문서입니다.
작업 시작 전 반드시 이 문서를 먼저 읽으세요.

---

## 프로젝트 개요

**서비스명:** 도서 추천 플랫폼
**설명:** 사용자가 자신의 취향을 입력하면, 맞춤 도서를 추천하고 동시에 리뷰, 최저가 온라인 서점 연결, 가까운 도서관 위치까지 한 화면에서 비교·확인할 수 있는 웹 서비스

**주요 기능:**
- 장르별 도서 탐색 (탐색·열람)
- 맞춤 도서 추천 (취향·관심사·기본 정보 입력 기반)
- 평점·리뷰 작성 (방명록 형태)
- 온라인 서점 최저가 비교 및 링크 제공
- 서울시 도서관 위치 지도 표시

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Frontend | React, TypeScript |
| Database | SQLite (개발), 추후 PostgreSQL 전환 검토 |
| External API | OpenAPI (서점/도서관), Map API |
| 버전 관리 | GitHub |
| 협업 도구 | Notion |
| 배포 | AWS (EC2 or 컨테이너 기반) |

---

## 디렉토리 구조

```
se_backend/
├── CLAUDE.md                  # AI 업무지침서 (현재 파일)
├── ARCHITECTURE.md            # 시스템 전체 구조
├── manage.py
├── requirements.txt
├── pyproject.toml             # 코드 스타일 설정
├── .pre-commit-config.yaml    # 프리커밋 훅
├── .env                       # 환경변수 (git 제외)
├── .env.example               # 환경변수 예시 (git 포함)
│
├── .claude/
│   └── settings.json          # AI 권한 설정
│
├── .github/
│   └── workflows/
│       └── ci.yml             # CI 자동화
│
├── config/                    # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── docs/
│   ├── SECURITY.md
│   ├── QUALITY_SCORE.md
│   └── RELIABILITY.md
│
└── {app_name}/                # 기능별 앱 (추후 추가)
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── tests.py
```

---

## 브랜치 전략

| 브랜치 | 용도 |
|---|---|
| `main` | 배포 가능 상태만 유지 |
| `develop` | 개발 통합 브랜치 |
| `feature/{기능명}` | 기능 단위 개발 |

- **PR은 반드시 `develop`으로** 올리고, 검토 후 `main`에 머지
- 브랜치 이름 예시: `feature/book-recommendation`, `feature/library-map`

---

## 개발 규칙

### 앱 구조
- 기능 단위로 Django 앱을 분리: `python manage.py startapp {앱이름}`
- 각 앱은 `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py` 포함

### API 설계
- 모든 API는 `/api/v1/` prefix 사용
- RESTful 규칙 준수 (GET/POST/PUT/PATCH/DELETE)
- 응답 형식은 항상 JSON

### 코드 스타일
- **black**: 코드 자동 포맷팅 (line-length 88)
- **flake8**: 코드 품질 검사
- **isort**: import 자동 정렬
- 커밋 전 pre-commit 훅이 자동 실행됨

### 네이밍 컨벤션
- 변수/함수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- URL: `kebab-case` (예: `/api/v1/book-recommendations/`)

---

## 환경변수 관리

- 모든 민감 정보는 `.env` 파일에 저장, **절대 git에 커밋하지 않음**
- 외부 API 키(서점, Map API 등) 포함
- `.env.example`에 키 목록만 작성하여 git에 포함

```
# .env.example
SECRET_KEY=
DEBUG=
MAP_API_KEY=
BOOKSTORE_API_KEY=
```

---

## 품질 관리 (4-Stage Quality Gate)

| 단계 | 시점 | 방법 |
|---|---|---|
| 1. 로컬 검증 | 코드 작성 후 | pre-commit 훅 (black, flake8) |
| 2. 자동 검증 | PR 생성 시 | GitHub Actions CI (테스트, 린트) |
| 3. 통합 환경 검증 | 머지 후 | develop 브랜치 통합 테스트 |
| 4. 수동 데모 검증 | Sprint 종료 | 팀 전체 데모 확인 |

---

## AI 에이전트 주의사항

- `.env` 파일을 절대 읽거나 출력하지 않음
- 외부 API 키를 코드에 하드코딩하지 않음
- `main` 브랜치에 직접 커밋하지 않음
- DB 마이그레이션 파일은 자동 생성 후 반드시 내용 확인
- 패키지 추가 시 `requirements.txt` 업데이트 필수
- 테스트 없이 새 기능을 완료 처리하지 않음
