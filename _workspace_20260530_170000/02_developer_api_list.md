# API 구현 결과: recommendations 앱

## 1. 작업 개요
- 대상 앱: `recommendations`
- 담당: drf-developer
- 입력 인계: `_workspace/02_architect_models.md` (django-architect)
- 구현 방식: Stateless — DB 모델 없이 OpenAI GPT(`gpt-4o`) 호출 결과를 그대로 응답

---

## 2. 구현된 파일 목록

| 파일 | 역할 |
|------|------|
| `recommendations/serializers.py` | `RecommendationRequestSerializer` — 8개 폼 필드 유효성 검사 (book_type/장르/관심사/목적/분위기/난이도/선호/회피) |
| `recommendations/services.py` | `build_prompt`, `get_book_recommendations` — 한국어 프롬프트 빌더 및 OpenAI API 호출 |
| `recommendations/views.py` | `RecommendationView(APIView)` — POST 처리, 400/200/503 응답 분기 |
| `recommendations/urls.py` | `path("", RecommendationView.as_view(), name="recommendation")` |
| `config/urls.py` | `path("api/v1/recommendations/", include("recommendations.urls"))` 등록 |

---

## 3. API 엔드포인트 명세

### 3.1. 도서 추천 요청

- **URL**: `/api/v1/recommendations/`
- **Method**: `POST`
- **Permission**: `AllowAny` (인증 불필요)
- **Content-Type**: `application/json`

#### 요청 바디

| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| `book_type` | string | 필수 | `"FICTION"` 또는 `"NONFICTION"` |
| `genres` | string[] | 필수 | book_type에 맞는 장르 코드만 허용, 최소 1개 |
| `interests` | string[] | 선택 | `INTEREST_CHOICES`에 포함된 값 |
| `interests_other` | string | 조건부 | `interests`에 `"other"` 포함 시 필수 |
| `purpose` | string[] | 선택 | `PURPOSE_CHOICES`에 포함된 값 |
| `purpose_other` | string | 조건부 | `purpose`에 `"other"` 포함 시 필수 |
| `mood` | string[] | 선택 | `MOOD_CHOICES` 값. **NONFICTION일 경우 무시되어 빈 배열로 덮어씀** |
| `difficulty` | string[] | 선택 | `DIFFICULTY_CHOICES` 값 |
| `favorite_books` | string | 선택 | 자유 텍스트 |
| `avoid_elements` | string | 선택 | 자유 텍스트 |

##### 허용 선택지

- **FICTION_GENRES**: `romance, fantasy, sf, mystery, thriller, horror, historical, coming_of_age, family, human_drama, classic, contemporary`
- **NONFICTION_GENRES**: `humanities, psychology, self_help, economics, social_political, history, science, tech_it, arts_culture, travel, health, education, religion`
- **INTEREST_CHOICES**: `relationships, love, growth, comfort, self_esteem, psychology, meaning_of_life, money_investment, career, social_issues, history, science_tech, arts_creation, travel, mystery, new_world, other`
- **PURPOSE_CHOICES**: `immersion, mood_change, comfort, knowledge, contemplation, light_read, deep_read, assignment, new_taste, other`
- **MOOD_CHOICES** (FICTION 전용): `warm, dark, emotional, cheerful, calm, philosophical, tense, realistic, dreamy, hopeful, sad`
- **DIFFICULTY_CHOICES**: `very_easy, moderate, literary, professional, deep, short_light, long_ok`

#### 요청 예시 (FICTION)

```json
{
  "book_type": "FICTION",
  "genres": ["romance", "contemporary"],
  "interests": ["love", "growth"],
  "purpose": ["immersion", "comfort"],
  "mood": ["warm", "emotional"],
  "difficulty": ["moderate", "short_light"],
  "favorite_books": "정세랑 - 보건교사 안은영",
  "avoid_elements": "잔혹한 묘사"
}
```

#### 요청 예시 (NONFICTION + other)

```json
{
  "book_type": "NONFICTION",
  "genres": ["psychology", "self_help"],
  "interests": ["self_esteem", "other"],
  "interests_other": "명상과 마음챙김",
  "purpose": ["knowledge"],
  "difficulty": ["moderate"]
}
```

#### 성공 응답 (200 OK)

```json
{
  "recommendations": [
    {
      "title": "달러구트 꿈 백화점",
      "author": "이미예",
      "reason": "따뜻하고 감성적인 분위기를 선호하며 위로와 몰입을 원하는 독자에게 부담 없이 다가오는 판타지 소설입니다. 일상에서 잠시 벗어나 꿈이라는 새로운 세계로 안내합니다."
    }
    // ... 총 5개
  ]
}
```

#### 에러 응답

| 상태 코드 | 상황 | 응답 형태 |
|-----------|------|----------|
| `400 Bad Request` | 입력 유효성 검사 실패 | `serializer.errors` (필드명: 오류 메시지) |
| `503 Service Unavailable` | OpenAI API 호출 실패 또는 응답 파싱 실패 | `{"error": "추천 서비스 오류가 발생했습니다."}` |

##### 400 응답 예시

```json
{
  "genres": ["FICTION에서 허용되지 않는 장르입니다: ['humanities']. 허용 값: [...]"]
}
```

```json
{
  "interests_other": ["interests에 'other'가 포함된 경우 interests_other 값을 입력해야 합니다."]
}
```

---

## 4. 유효성 검사 규칙 요약 (Serializer)

1. `book_type=FICTION` → `genres` 항목이 모두 `FICTION_GENRES`여야 함
2. `book_type=NONFICTION` → `genres` 항목이 모두 `NONFICTION_GENRES`여야 함
3. `book_type=NONFICTION` → `mood`는 무시되고 `[]`로 덮어쓰여진 채 GPT에 전달
4. `interests`에 `"other"` 포함 시 `interests_other` 비어있으면 400
5. `purpose`에 `"other"` 포함 시 `purpose_other` 비어있으면 400
6. `interests` 항목은 `INTEREST_CHOICES` 내 값만 허용
7. `purpose` 항목은 `PURPOSE_CHOICES` 내 값만 허용
8. (FICTION) `mood` 항목은 `MOOD_CHOICES` 내 값만 허용
9. `difficulty` 항목은 `DIFFICULTY_CHOICES` 내 값만 허용

---

## 5. 외부 패키지 / 의존성

| 패키지 | 용도 |
|--------|------|
| `djangorestframework` | API 직렬화/뷰 |
| `openai` (>=2.38.0) | OpenAI GPT API 호출 (Chat Completions, JSON mode) |

### 환경변수 (`.env`)

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI 비밀 키 (필수, 운영자 주입) | 없음 |
| `OPENAI_MODEL` | 사용할 모델명 | `gpt-4o` |

> 코드 내 하드코딩 금지 — `os.getenv("OPENAI_API_KEY")` 방식으로만 로드한다.

---

## 6. 서비스 동작 흐름

1. 클라이언트가 `POST /api/v1/recommendations/`로 JSON 폼 데이터 전송
2. `RecommendationRequestSerializer.is_valid()` → 실패 시 **400** 반환
3. `services.build_prompt(validated_data)` → 한국어 자연어 프롬프트 생성
   - 영문 코드(`romance`, `warm` 등)는 `services.py`의 한국어 매핑 딕셔너리(`BOOK_TYPE_KO`, `GENRE_KO`, `INTEREST_KO`, `PURPOSE_KO`, `MOOD_KO`, `DIFFICULTY_KO`)로 변환
4. `services.get_book_recommendations()` → OpenAI Chat Completions 호출 (`response_format=json_object`, `temperature=0.7`)
5. 응답 JSON 파싱 후 `recommendations` 배열 추출
6. 성공: **200**으로 `{"recommendations": [...]}` 반환
7. 예외 발생 시 **503**으로 일반화된 에러 메시지 반환 (스택트레이스 미노출)

---

## 7. 검증 결과

| 항목 | 결과 |
|------|------|
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `black --line-length 88` | 모든 대상 파일 통과 (재포맷 1건 적용 후 통과) |
| `isort` | 모든 대상 파일 통과 |
| `flake8` | 위반 없음 |
| URL reverse(`recommendation`) | `/api/v1/recommendations/` 정상 해석 |

---

## 8. test-quality-engineer 인계 사항

### 권장 테스트 시나리오

1. **정상 케이스**
   - FICTION 정상 요청 → 200, `recommendations` 5개 (mocking 가능)
   - NONFICTION 정상 요청 → 200, mood 자동 무시
2. **유효성 검사 실패**
   - `book_type` 누락 → 400
   - `genres` 빈 배열 → 400
   - FICTION에 `humanities`(NONFICTION 전용) 포함 → 400
   - `interests=['other']` & `interests_other=''` → 400
   - `purpose=['other']` & `purpose_other=''` → 400
   - `mood` 잘못된 값 (FICTION) → 400
   - `difficulty` 잘못된 값 → 400
3. **외부 API 오류**
   - `openai.OpenAI` 모킹하여 예외 발생 → 503

### 모킹 가이드

- `recommendations.services.get_book_recommendations`를 모킹하거나
- `openai.OpenAI`를 패치하여 OpenAI 실제 호출 없이 테스트 (실제 키 노출 방지)

---

## 9. 산출물 위치

- `c:\Users\김석준\Desktop\se_backend\recommendations\serializers.py`
- `c:\Users\김석준\Desktop\se_backend\recommendations\services.py`
- `c:\Users\김석준\Desktop\se_backend\recommendations\views.py`
- `c:\Users\김석준\Desktop\se_backend\recommendations\urls.py`
- `c:\Users\김석준\Desktop\se_backend\config\urls.py` (수정됨)
- `c:\Users\김석준\Desktop\se_backend\_workspace\02_developer_api_list.md` (본 문서)
