# 요구사항 명세서 — libraries 앱

## 작업 개요

서울 열린데이터 광장 API(SeoulPublicLibraryInfo)와 네이버 지도 API를 활용하여
서울시 공공 도서관 위치 정보를 제공하는 `libraries` Django 앱을 신규 생성한다.

---

## 환경변수

| 변수명 | 용도 |
|---|---|
| `SEOUL_API_KEY` | 서울 열린데이터 광장 인증키 |
| `NAVER_MAP_CLIENT_ID` | 네이버 지도 Client ID (프론트엔드에 전달) |

---

## 모델: `Library`

| 필드 | 타입 | 비고 |
|---|---|---|
| `name` | CharField(max_length=200) | 도서관명 |
| `address` | CharField(max_length=300) | 도로명 주소 |
| `latitude` | FloatField | 위도 |
| `longitude` | FloatField | 경도 |
| `phone` | CharField(max_length=50, blank=True) | 전화번호 |
| `homepage` | URLField(blank=True) | 홈페이지 URL |
| `updated_at` | DateTimeField(auto_now=True) | 최종 동기화 시각 |

---

## 서울 열린데이터 광장 API

- 데이터셋: `SeoulPublicLibraryInfo`
- 엔드포인트: `http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/SeoulPublicLibraryInfo/1/1000/`
- 주요 응답 필드:

| 응답 필드 | 모델 필드 |
|---|---|
| `LBRRY_NAME` | `name` |
| `ADRES` | `address` |
| `XCNTS` | `longitude` |
| `YDNTS` | `latitude` |
| `TEL_NO` | `phone` |
| `HMPG_URL` | `homepage` |

---

## API 엔드포인트

### 1. `GET /api/v1/libraries/`
- **목적**: 서울시 도서관 전체 목록 반환 (위·경도 포함)
- **DB 캐시 로직**:
  - `Library` 레코드 중 `updated_at` 날짜가 오늘인 것이 1개 이상 → DB 반환
  - 없거나 오래됐으면 Seoul API 호출 → `Library.objects.update_or_create(name=...)` → DB 반환
- **성공 응답 (200)**:
```json
[
  {
    "id": 1,
    "name": "강남도서관",
    "address": "서울특별시 강남구 ...",
    "latitude": 37.5172,
    "longitude": 127.0473,
    "phone": "02-1234-5678",
    "homepage": "https://example.go.kr"
  }
]
```
- **에러 응답**:
  - 503: Seoul API 키 미설정 또는 호출 실패

### 2. `GET /api/v1/libraries/{id}/`
- **목적**: 도서관 상세 정보
- **성공 응답 (200)**: 단일 Library 객체
- **에러 응답**: 404

### 3. `GET /api/v1/libraries/map-config/`
- **목적**: 프론트엔드에 네이버 지도 Client ID 전달
- **성공 응답 (200)**:
```json
{ "naver_map_client_id": "abc123" }
```
- **에러 응답**:
  - 503: NAVER_MAP_CLIENT_ID 미설정

---

## 서비스 레이어 (`libraries/services.py`)

```python
def fetch_libraries_from_api() -> list[dict]:
    """서울 열린데이터 광장 API 호출 → 파싱된 도서관 dict 리스트 반환"""

def sync_libraries() -> QuerySet:
    """DB 캐시 확인 → 필요시 fetch_libraries_from_api() 호출 → upsert → QuerySet 반환"""
```

---

## 테스트 시나리오 (`libraries/tests.py`)

| 테스트 | 내용 |
|---|---|
| `test_list_from_db_cache` | DB에 오늘 날짜 레코드 존재 → API 미호출, 200 반환 |
| `test_list_calls_api_when_no_cache` | DB 비어있음 → Seoul API mock 호출 → 200 반환 |
| `test_list_no_api_key` | SEOUL_API_KEY 없음 → 503 |
| `test_detail_success` | 존재하는 id → 200 |
| `test_detail_not_found` | 존재하지 않는 id → 404 |
| `test_map_config_success` | NAVER_MAP_CLIENT_ID 설정됨 → 200, 키 반환 |
| `test_map_config_no_key` | NAVER_MAP_CLIENT_ID 없음 → 503 |

---

## URL 구조

```
config/urls.py
└── /api/v1/libraries/  → libraries.urls
        ├── (list)           → LibraryListView
        ├── map-config/      → LibraryMapConfigView
        └── {id}/            → LibraryDetailView
```

**주의**: `map-config/`를 `{id}/` 보다 먼저 등록해야 충돌 없음

---

## 완료 조건

- [ ] `uv run python manage.py startapp libraries` 실행
- [ ] `config/settings.py` INSTALLED_APPS에 `"libraries"` 등록
- [ ] `Library` 모델 + 마이그레이션 완료
- [ ] `services.py`, `serializers.py`, `views.py`, `urls.py` 구현
- [ ] `config/urls.py`에 `api/v1/libraries/` 등록
- [ ] `.env.example`에 `SEOUL_API_KEY=`, `NAVER_MAP_CLIENT_ID=` 추가
- [ ] 테스트 7개 모두 PASS
- [ ] pre-commit 통과
