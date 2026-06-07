# 모델 설계 요약 — libraries 앱

## 앱 이름

`libraries`

---

## 모델명 및 필드 목록

### `Library`

| 필드 | 타입 | 옵션 | verbose_name |
|---|---|---|---|
| `id` | BigAutoField | PK (자동 생성) | ID |
| `name` | CharField(max_length=200) | — | 도서관명 |
| `address` | CharField(max_length=300) | — | 도로명 주소 |
| `latitude` | FloatField | — | 위도 |
| `longitude` | FloatField | — | 경도 |
| `phone` | CharField(max_length=50) | blank=True | 전화번호 |
| `homepage` | URLField | blank=True | 홈페이지 URL |
| `updated_at` | DateTimeField | auto_now=True | 최종 동기화 시각 |

**Meta:**
- `ordering = ["name"]`
- `verbose_name = "도서관"`
- `verbose_name_plural = "도서관 목록"`

**`__str__`:** `return self.name`

---

## 마이그레이션 파일명

`libraries/migrations/0001_initial.py`

- 생성 일시: 2026-06-01
- 작업: `Create model Library`
- 의존성: 없음 (초기 마이그레이션)

---

## INSTALLED_APPS 등록 여부

`config/settings.py`의 `INSTALLED_APPS`에 `"libraries"` 등록 완료.

```python
INSTALLED_APPS = [
    ...
    "recommendations",
    "bookstores",
    "libraries",   # 추가됨
]
```

---

## URL 라우팅 구조 (예정)

`config/urls.py`에 등록 예정:

```
/api/v1/libraries/            → libraries.urls
    (list)                    → LibraryListView
    map-config/               → LibraryMapConfigView
    {id}/                     → LibraryDetailView
```

**주의:** `map-config/`를 `{id}/` 앞에 등록해야 URL 충돌 없음.

---

## 다음 단계 (drf-developer 전달 사항)

- `libraries/serializers.py`: `LibrarySerializer` 구현 (`id`, `name`, `address`, `latitude`, `longitude`, `phone`, `homepage` 직렬화)
- `libraries/services.py`: `fetch_libraries_from_api()`, `sync_libraries()` 구현
- `libraries/views.py`: `LibraryListView`, `LibraryDetailView`, `LibraryMapConfigView` 구현
- `libraries/urls.py`: 위 뷰 연결 (map-config/ 먼저 등록)
- `config/urls.py`: `/api/v1/libraries/` include 추가
- `.env.example`: `SEOUL_API_KEY=`, `NAVER_MAP_CLIENT_ID=` 추가
- `libraries/tests.py`: 7개 테스트 시나리오 구현
