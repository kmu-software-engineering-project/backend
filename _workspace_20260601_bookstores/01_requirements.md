# 요구사항 명세서

## 작업 개요

GPT 기반 도서 추천 시스템에 두 가지 기능을 추가한다.

1. **추천 API ISBN 필드 추가**: 기존 recommendations 앱의 GPT 응답에 isbn 필드 추가
2. **bookstores 앱 신규 생성**: 네이버 쇼핑 API 기반 서점별 가격 비교 API 구현

---

## 현재 구현 상태

- `recommendations` 앱 존재
- `POST /api/v1/recommendations/` 구현됨
- `recommendations/services.py`의 `get_book_recommendations()`가 OpenAI GPT API 호출
- 현재 응답: `[{"title": str, "author": str, "reason": str}, ...]`

---

## Task 1. recommendations 앱 수정 — ISBN 필드 추가

### 대상 파일
- `recommendations/services.py`

### 변경 내용
- `get_book_recommendations()` 내 GPT system prompt 수정
- `isbn` 필드를 JSON 응답에 포함하도록 요청
- ISBN을 모를 경우 `null` 반환 허용

### 변경 후 GPT 응답 구조
```json
{
  "recommendations": [
    {
      "title": "채식주의자",
      "author": "한강",
      "reason": "추천 이유 (2-3문장)",
      "isbn": "9788936433598"
    }
  ]
}
```

### 수정할 system_prompt 내용
- 기존: `{"title": "책 제목", "author": "저자명", "reason": "추천 이유"}`
- 변경: `{"title": "책 제목", "author": "저자명", "reason": "추천 이유", "isbn": "ISBN 13자리 숫자 (모를 경우 null)"}`

---

## Task 2. bookstores 앱 신규 생성

### 앱 정보
- 앱 이름: `bookstores`
- INSTALLED_APPS 등록 필요: `"bookstores"`

### 모델
- DB 모델 없음 (외부 API 연동만 수행)

### API 엔드포인트

#### `GET /api/v1/bookstores/prices/`

**목적:** 네이버 쇼핑 API를 통해 책의 서점별 가격 비교 정보 반환

**쿼리 파라미터:**
| 파라미터 | 필수 여부 | 설명 |
|----------|----------|------|
| `title` | 필수 | 책 제목 |
| `author` | 선택 | 저자명 (검색 정확도 향상) |
| `isbn` | 선택 | ISBN 13자리 (있으면 우선 사용) |

**처리 로직:**
1. `isbn`이 있으면 isbn으로 검색, 없으면 `title + author`로 검색
2. 네이버 쇼핑 검색 API 호출:
   - URL: `https://openapi.naver.com/v1/search/shop.json`
   - 헤더: `X-Naver-Client-Id`, `X-Naver-Client-Secret`
   - 파라미터: `query={검색어}`, `display=30`, `sort=sim`
3. 결과에서 각 서점별 최저가 추출 (동일 서점 중복 시 가장 낮은 가격 선택)
4. 가격 오름차순 정렬

**성공 응답 (200 OK):**
```json
{
  "book": {
    "title": "채식주의자",
    "author": "한강"
  },
  "stores": [
    {
      "store_name": "알라딘",
      "price": 12600,
      "purchase_url": "https://www.aladin.co.kr/..."
    },
    {
      "store_name": "YES24",
      "price": 12800,
      "purchase_url": "https://www.yes24.com/..."
    },
    {
      "store_name": "교보문고",
      "price": 13500,
      "purchase_url": "https://product.kyobobook.co.kr/..."
    }
  ]
}
```

**에러 응답:**
| 상황 | HTTP 코드 | 응답 |
|------|----------|------|
| `title` 파라미터 누락 | 400 | `{"error": "title 파라미터가 필요합니다."}` |
| 네이버 API 키 미설정 | 503 | `{"error": "가격 비교 서비스를 사용할 수 없습니다."}` |
| 네이버 API 호출 실패 | 503 | `{"error": "가격 비교 서비스를 사용할 수 없습니다."}` |
| 검색 결과 없음 | 200 | `{"book": {...}, "stores": []}` |

### 서비스 레이어 (`bookstores/services.py`)

```python
def get_book_prices(title: str, author: str = "", isbn: str = "") -> list:
    """
    네이버 쇼핑 API로 서점별 최저가 조회.
    반환: [{"store_name": str, "price": int, "purchase_url": str}, ...]
    """
```

### 환경변수
`.env.example`에 추가:
```
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

---

## Task 3. 테스트

### bookstores/tests.py
1. 정상 응답 테스트: 네이버 API mock → 여러 서점 가격 반환 확인
2. title 파라미터 누락 테스트: 400 응답 확인
3. 검색 결과 없음 테스트: `stores: []` 반환 확인
4. 동일 서점 중복 시 최저가 선택 테스트

### recommendations/tests.py
- isbn 필드 포함 여부 테스트 추가 (GPT mock 응답에 isbn 포함)

---

## URL 구조

```
config/urls.py
├── /api/v1/recommendations/  → recommendations.urls
└── /api/v1/bookstores/       → bookstores.urls
        └── prices/           → BookPriceView
```

---

## 코드 스타일
- black (line-length 88)
- flake8
- isort
- pre-commit 훅 통과 필수
