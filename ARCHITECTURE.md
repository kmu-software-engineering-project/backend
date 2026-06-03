# ARCHITECTURE.md — 시스템 전체 구조 개요

---

## 서비스 구조

```
[ Next.js + TypeScript ]  ←→  [ Django REST Framework ]  ←→  [ SQLite / PostgreSQL ]
   Frontend (포트 3000)          Backend (포트 8000)                Database

                                       ↕
                            [ 외부 API ]
                            - OpenAI API (GPT 도서 추천)
                            - 네이버 도서 검색 API (서점 가격 비교)
                            - 서울 열린데이터 도서관 API (도서관 위치)
                            - Kakao 지도 JavaScript API (지도 표시)
                            - Kakao 도서 검색 API (프론트엔드)
                            - Aladin TTB API (프론트엔드)
                            - 국립중앙도서관 사서 추천 API (프론트엔드)
```

---

## 기술 스택

| 구분 | 기술 | 비고 |
|---|---|---|
| Frontend | Next.js 16, React 18, TypeScript | 포트 3000 |
| Backend | Django 5.2, DRF | 포트 8000 |
| Database | SQLite | 개발용, 운영은 PostgreSQL 검토 |
| External API | OpenAI, 네이버, 서울시 공공데이터, Kakao, Aladin | 환경변수로 키 관리 |
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
├── recommendations/         # GPT 맞춤 도서 추천
├── reviews/                 # 평점·리뷰 작성 (방명록)
├── libraries/               # 서울시 도서관 위치
├── bookstores/              # 온라인 서점 가격 비교
│
├── docs/
├── .github/workflows/
├── manage.py
├── pyproject.toml
└── uv.lock
```

각 앱은 `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py` 구조를 따릅니다.

---

## 앱 구성 현황

| 앱 이름 | 상태 | 담당 기능 |
|---|---|---|
| `recommendations` | ✅ 구현 완료 | GPT 기반 맞춤 도서 추천 |
| `reviews` | ✅ 구현 완료 | 평점·리뷰 작성 (방명록, 비밀번호 보호) |
| `libraries` | ✅ 구현 완료 | 서울시 도서관 위치 (서울 열린데이터 API) |
| `bookstores` | ✅ 구현 완료 | 온라인 서점 가격 비교 (네이버 도서 API) |
| `books` | ⬜ 미구현 | 도서 정보, 장르별 탐색 (계획) |

---

## 구현된 API 엔드포인트

### recommendations
| Method | URL | 설명 |
|---|---|---|
| `POST` | `/api/v1/recommendations/` | 취향 폼 입력 → GPT 도서 5권 추천 |

### reviews
| Method | URL | 설명 |
|---|---|---|
| `GET` | `/api/v1/reviews/?book_id={id}&ordering=latest\|rating` | 리뷰 목록 (최신순 / 평점 높은순) |
| `POST` | `/api/v1/reviews/` | 리뷰 작성 (닉네임, 비밀번호, 별점 1~5, 한 줄 평) |
| `DELETE` | `/api/v1/reviews/{id}/` | 리뷰 삭제 (비밀번호 body 검증) |

### libraries
| Method | URL | 설명 |
|---|---|---|
| `GET` | `/api/v1/libraries/` | 서울시 공공 도서관 목록 |
| `GET` | `/api/v1/libraries/{id}/` | 도서관 상세 정보 |
| `GET` | `/api/v1/libraries/map-config/` | 카카오 지도 API 키 제공 |

### bookstores
| Method | URL | 설명 |
|---|---|---|
| `GET` | `/api/v1/bookstores/prices/?title={제목}` | 서점별 가격 비교 및 구매 링크 |

### 공통
| URL | 설명 |
|---|---|
| `GET /api/schema/` | OpenAPI 스키마 |
| `GET /api/docs/` | Swagger UI |

---

## API 설계 원칙

- 모든 엔드포인트는 `/api/v1/` prefix 사용
- RESTful 규칙 준수 (GET / POST / DELETE)
- 응답 형식은 항상 JSON
- 인증 없음 (`AllowAny`) — 로그인/회원가입 없는 서비스
- 필드명은 camelCase 사용 (`bookId`, `bookTitle`, `createdAt` 등) — 프론트엔드 TypeScript 타입과 통일

---

## 프론트엔드-백엔드 통신

- CORS: 개발 환경 전체 허용 (`DEBUG=True`), 프로덕션 `http://localhost:3000`
- 데이터 형식: JSON
- 프론트엔드 Next.js API 라우트(`/app/api/`)가 백엔드를 프록시하는 방식으로 호출
- `BACKEND_URL` 환경변수로 백엔드 주소 설정 (기본값: `http://localhost:8000`)

---

## 보안 고려사항

- 리뷰 비밀번호: DB 저장 시 Django `make_password()` 해시 처리, 응답에 미포함
- API 키: `.env` 파일 관리, git 제외
- 인증이 필요한 기능 없음 (방명록 형태 서비스)
