# 모델 설계 요약 — reviews 앱

## 앱 이름

`reviews`

---

## 모델명 및 필드 목록

### `Review`

| 필드 | 타입 | 옵션 | verbose_name |
|---|---|---|---|
| `id` | BigAutoField | PK (자동 생성) | ID |
| `book_id` | CharField(max_length=200) | db_index=True | 도서 ID |
| `book_title` | CharField(max_length=500) | — | 도서 제목 |
| `nickname` | CharField(max_length=50) | — | 닉네임 |
| `password` | CharField(max_length=128) | — | 비밀번호 |
| `rating` | PositiveSmallIntegerField | MinValueValidator(1), MaxValueValidator(5) | 별점 |
| `comment` | CharField(max_length=100) | — | 한 줄 평 |
| `created_at` | DateTimeField | auto_now_add=True | 작성 시각 |

**설계 결정 사항:**
- `book_id`에 `db_index=True` 적용 — 리뷰 목록 조회가 항상 `book_id` 기준 필터링이므로 인덱스 필수
- `password`는 `max_length=128` — Django `make_password()` 해시 결과 길이에 맞춤
- `updated_at` 미포함 — 리뷰는 수정 기능 없음(작성·삭제만 지원)
- `rating`은 `PositiveSmallIntegerField` — 1~5 범위, 작은 정수형으로 충분

**Meta:**
- `ordering = ["-created_at"]` (기본 최신순)
- `verbose_name = "리뷰"`
- `verbose_name_plural = "리뷰 목록"`

**`__str__`:** `return f"[{self.rating}★] {self.nickname} - {self.book_title[:30]}"`

---

## 마이그레이션 파일명

`reviews/migrations/0001_initial.py`

- 생성 일시: 2026-06-03 06:15 (Django 5.2.14 자동 생성)
- 작업: `Create model Review`
- 의존성: 없음 (초기 마이그레이션)

---

## INSTALLED_APPS 등록 여부

`config/settings.py`의 `INSTALLED_APPS`에 `"reviews"` 등록 완료.

---

## URL 라우팅 구조

`config/urls.py`에 등록:

```
/api/v1/reviews/       → reviews.urls
    (list/create)      → ReviewListCreateView  (GET, POST)
    {id}/              → ReviewDeleteView       (DELETE)
```

**ViewSet 미사용 이유:** 목록 조회·작성은 같은 URL, 삭제는 별도 URL이며 CRUD 중 일부만 구현하므로 `APIView`를 직접 사용.

---

## 다음 단계 (drf-developer 전달 사항)

- `reviews/serializers.py`:
  - `ReviewSerializer` — 조회 응답용, password 미포함, camelCase 필드명
  - `ReviewCreateSerializer` — 작성 입력용, password write_only, 저장 시 make_password() 처리
  - `ReviewDeleteSerializer` — 삭제 비밀번호 검증용, check_password() 사용
- `reviews/views.py`:
  - `ReviewListCreateView` — GET(목록, book_id 필터+ordering), POST(작성)
  - `ReviewDeleteView` — DELETE(비밀번호 검증 후 삭제)
- `reviews/urls.py`: 위 뷰 연결
- `config/urls.py`: `/api/v1/reviews/` include 추가
