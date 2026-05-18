# ARCHITECTURE.md — 시스템 전체 구조 개요

---

## 서비스 구조

```
[ React + TypeScript ]  ←→  [ Django REST Framework ]  ←→  [ SQLite / PostgreSQL ]
      Frontend                      Backend                       Database

                                       ↕
                            [ 외부 API ]
                            - OpenAPI (서점/도서관)
                            - Map API (서울시 도서관 위치)
```

---

## 기술 스택

| 구분 | 기술 | 비고 |
|---|---|---|
| Frontend | React, TypeScript | 포트 3000 |
| Backend | Django 5.2, DRF | 포트 8000 |
| Database | SQLite | 개발용, 운영은 PostgreSQL 검토 |
| External API | OpenAPI, Map API | 환경변수로 키 관리 |
| 배포 | AWS EC2 or 컨테이너 | 추후 결정 |
| CI/CD | GitHub Actions | PR 시 자동 실행 |

---

## 백엔드 디렉토리 구조

```
se_backend/
├── config/                  # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py              # 루트 URL (api/v1/ prefix)
│   └── wsgi.py
│
├── {app}/                   # 기능별 앱 (예시)
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── docs/
├── .github/workflows/
├── manage.py
├── pyproject.toml
└── uv.lock
```

---

## 앱 구성 계획

| 앱 이름 | 담당 기능 |
|---|---|
| `books` | 도서 정보, 장르별 탐색 |
| `recommendations` | 맞춤 도서 추천 |
| `reviews` | 평점·리뷰 작성 |
| `libraries` | 서울시 도서관 위치 (Map API) |
| `bookstores` | 온라인 서점 최저가 비교 |

---

## API 설계 원칙

- 모든 엔드포인트는 `/api/v1/` prefix 사용
- RESTful 규칙 준수
- 응답 형식은 항상 JSON
- 인증 없음 (`AllowAny`) — 로그인/회원가입 없는 서비스

### 엔드포인트 예시

```
GET  /api/v1/books/                  # 도서 목록
GET  /api/v1/books/{id}/             # 도서 상세
GET  /api/v1/recommendations/        # 맞춤 추천
POST /api/v1/reviews/                # 리뷰 작성
GET  /api/v1/libraries/              # 도서관 목록
GET  /api/v1/bookstores/{book_id}/   # 서점별 가격 비교
```

---

## 프론트엔드-백엔드 통신

- CORS 허용: `http://localhost:3000` (개발 환경)
- 데이터 형식: JSON
- 프론트엔드에서 `fetch` 또는 `axios`로 API 호출
