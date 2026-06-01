# 아키텍처 설계 결과: recommendations 앱

## 1. 작업 개요
- 대상 앱: `recommendations`
- 목적: 사용자 취향 폼 입력 기반 OpenAI GPT(gpt-4o) 호출로 맞춤 도서 5권 추천
- 저장 방식: **Stateless (DB 모델 없음)**
- 담당: django-architect

---

## 2. 생성된 앱 구조

```
recommendations/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py        # 기본 상태 유지 (Stateless이므로 모델 미정의)
├── tests.py
└── views.py
```

- 생성 명령: `uv run python manage.py startapp recommendations`
- 추가 예정 파일 (drf-developer 담당):
  - `recommendations/serializers.py`
  - `recommendations/services.py`
  - `recommendations/urls.py`

---

## 3. INSTALLED_APPS 등록

`config/settings.py`의 `INSTALLED_APPS`에 `"recommendations"` 등록 완료.

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "recommendations",   # 신규 등록
]
```

---

## 4. 패키지 의존성 추가

- 명령: `uv add openai`
- 결과: `pyproject.toml`의 `dependencies`에 `"openai>=2.38.0"` 추가 완료
- 설치된 버전: `openai==2.38.0`
- 연관 패키지 함께 설치: `pydantic`, `pydantic-core`, `httpx`, `httpcore`, `anyio`, `distro`, `jiter`, `tqdm` 등

---

## 5. 환경변수 파일 (.env.example)

기존 `.env.example` 파일이 부재하여 신규 생성하였으며 다음 두 항목 포함.

```
SECRET_KEY=
DEBUG=
MAP_API_KEY=
BOOKSTORE_API_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
```

- `OPENAI_API_KEY`: 운영자가 직접 주입할 OpenAI 비밀 키
- `OPENAI_MODEL`: 기본값 `gpt-4o`

> 주의: 실제 `.env` 파일은 git에 커밋되지 않으며, 운영자가 직접 OPENAI 키를 설정해야 한다.

---

## 6. 마이그레이션 결과

```
$ uv run python manage.py makemigrations recommendations
No changes detected in app 'recommendations'

$ uv run python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

- `recommendations` 앱은 모델이 없으므로 마이그레이션 파일 미생성 (정상)
- `migrations/__init__.py`만 존재하여 향후 모델 추가 시 즉시 마이그레이션 가능

---

## 7. drf-developer에게 전달할 모델 정보

### 데이터 모델
- **없음** — Stateless 설계로 인해 DB 모델을 정의하지 않음.
- 요청 데이터는 `serializers.py`에서 유효성 검사 후 OpenAI API에 전달, 응답을 그대로 JSON 직렬화하여 반환한다.

### 후속 구현 가이드 (drf-developer 인계)
1. **Serializer (`serializers.py`)**
   - `RecommendationRequestSerializer`: 폼 8개 필드 유효성 검사
   - 분기 로직: `book_type=FICTION` ↔ `NONFICTION`에 따라 `genres` 목록 제한
   - `interests`/`purpose`에 `other` 포함 시 각각 `interests_other`/`purpose_other` 필수
   - `book_type=NONFICTION`이면 `mood` 무시(None 처리)
   - 응답용 `RecommendationResponseSerializer`: `title`, `author`, `reason` 필드

2. **Service (`services.py`)**
   - 환경변수: `os.getenv("OPENAI_API_KEY")`, `os.getenv("OPENAI_MODEL", "gpt-4o")`
   - OpenAI SDK 호출 함수 `generate_recommendations(form_data: dict) -> list[dict]`
   - 시스템 프롬프트로 "맞춤 도서 5권 추천, JSON 형식 반환" 명시
   - 응답 파싱 후 5권의 `{title, author, reason}` 리스트 반환

3. **View (`views.py`)**
   - `RecommendationView(APIView)` — POST만 허용
   - `permission_classes = [AllowAny]`
   - 입력 유효성 검사 → 서비스 호출 → 응답 직렬화
   - 잘못된 입력: 400, OpenAI 호출 실패: 502 등 에러 핸들링

4. **URL (`recommendations/urls.py`)**
   - `path("", RecommendationView.as_view(), name="recommendations")`
   - 최종 엔드포인트: `POST /api/v1/recommendations/`

5. **config/urls.py 등록 필요**
   - `path("api/v1/recommendations/", include("recommendations.urls"))`

---

## 8. 다음 단계 (Handoff)

| 담당 | 작업 |
|------|------|
| drf-developer | serializers.py / services.py / views.py / urls.py 구현, config/urls.py 등록 |
| test-quality-engineer | tests.py 작성 (요구사항 문서의 6개 시나리오 기반) |

---

## 9. 검증 체크리스트

- [x] `recommendations` 앱 디렉토리 생성
- [x] `INSTALLED_APPS`에 등록
- [x] `models.py` 기본 상태 (Stateless)
- [x] `openai` 패키지 의존성 추가 (`uv add`)
- [x] `.env.example`에 `OPENAI_API_KEY`, `OPENAI_MODEL` 추가
- [x] `makemigrations` 실행 (No changes — 정상)
- [x] `migrate` 실행 완료
- [x] 외부 API 키 코드 하드코딩 없음 (`.env`에서만 로드)
