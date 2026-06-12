# 도서 추천 플랫폼 백엔드(with harness engineering)

소프트웨어공학 7팀 프로젝트입니다. 사용자 취향 기반 도서 추천, 리뷰, 온라인 서점 최저가 비교, 서울시 도서관 위치 안내를 제공하는 RESTful API 서버입니다. 또한, 하네스 엔지니어링(harness engineering)을 직접 프로젝트에 적용해가며 작업하였습니다.

## 하네스 엔지니어링

이 프로젝트는 AI 에이전트 팀이 함께하는 하네스 엔지니어링(harness engineering)을 직접 프로젝트에 적용하고 있습니다.
구성 요소, 실행 흐름, 에이전트 역할 등 상세 내용은 [harness.md](harness.md)를 참고하세요.

## 기술 스택

- **Framework:** Django 5.2, Django REST Framework
- **Database:** SQLite (개발)
- **External API:** OpenAI GPT-4o, 네이버 도서 검색, 서울시 공공데이터, Kakao Maps
- **패키지 관리:** uv
- **문서화:** drf-spectacular (Swagger UI)

## 프로젝트 구조

```
se_backend/
├── config/              # Django 프로젝트 설정 (settings.py, urls.py)
├── recommendations/     # GPT 기반 맞춤 도서 추천
├── reviews/             # 방명록 형태 평점·리뷰
├── libraries/           # 서울시 공공도서관 위치 조회
├── bookstores/          # 온라인 서점 최저가 비교
├── manage.py
├── pyproject.toml       # 의존성 정의
└── .env.example         # 환경변수 예시
```

## 시작하기

### 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 필요한 API 키 입력
```

필요한 환경변수:

| 변수명 | 설명 |
|---|---|
| `SECRET_KEY` | Django 시크릿 키 |
| `DEBUG` | 디버그 모드 (True/False) |
| `OPENAI_API_KEY` | OpenAI API 키 |
| `OPENAI_MODEL` | 사용할 모델 (기본값: gpt-4o) |
| `NAVER_CLIENT_ID` | 네이버 개발자센터 클라이언트 ID |
| `NAVER_CLIENT_SECRET` | 네이버 개발자센터 클라이언트 시크릿 |
| `SEOUL_API_KEY` | 서울 열린데이터광장 API 키 |
| `KAKAO_MAP_API_KEY` | Kakao 지도 JavaScript API 키 |

### 설치 및 실행

```bash
# 패키지 설치
uv sync --dev

# DB 마이그레이션
uv run python manage.py migrate

# 서버 실행 (http://localhost:8000)
uv run python manage.py runserver
```

### 테스트 및 린트

```bash
# 테스트 실행
uv run python manage.py test

# 린트 검사
uv run pre-commit run --all-files
```

## API 엔드포인트

모든 엔드포인트는 `/api/v1/` prefix를 사용합니다.

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| POST | `/recommendations/` | GPT 기반 맞춤 도서 5권 추천 |
| GET | `/reviews/?book_id={id}` | 특정 도서 리뷰 목록 조회 |
| POST | `/reviews/` | 리뷰 작성 (닉네임·비밀번호·별점·한 줄 평) |
| DELETE | `/reviews/{id}/` | 리뷰 삭제 (비밀번호 인증) |
| GET | `/libraries/` | 서울시 공공도서관 목록 |
| GET | `/libraries/{id}/` | 도서관 상세 정보 |
| GET | `/libraries/map-config/` | Kakao 지도 API 키 |
| GET | `/bookstores/prices/?isbn={isbn}` | 온라인 서점 최저가 및 구매 링크 |
| GET | `/docs/` | Swagger UI API 문서 |


## 주요 기능

- **도서 추천:** 장르, 관심사, 기분, 난이도 등 사용자 취향을 입력받아 GPT-4o가 5권 추천
- **리뷰:** 로그인 없이 닉네임과 비밀번호로 별점(1~5)과 한 줄 평 작성
- **최저가 비교:** 네이버 도서 API로 알라딘·교보·YES24·인터파크 구매 링크 제공
- **도서관 지도:** 서울시 공공데이터 API로 공공도서관 위치·연락처 조회
