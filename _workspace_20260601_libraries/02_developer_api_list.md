# API 엔드포인트 목록 — libraries 앱

## 구현 완료 일시
2026-06-01

---

## 엔드포인트 목록

| # | URL | HTTP 메서드 | 뷰 클래스 | 설명 |
|---|-----|------------|----------|------|
| 1 | `/api/v1/libraries/` | GET | `LibraryListView` | 서울시 공공 도서관 전체 목록 반환. 오늘 날짜 DB 캐시 있으면 반환, 없으면 Seoul API 호출 후 upsert |
| 2 | `/api/v1/libraries/map-config/` | GET | `LibraryMapConfigView` | 네이버 지도 Client ID 반환 (`NAVER_MAP_CLIENT_ID` 환경변수) |
| 3 | `/api/v1/libraries/<int:pk>/` | GET | `LibraryDetailView` | 지정 ID 도서관 상세 정보 반환 |

---

## 응답 형식

### `GET /api/v1/libraries/` — 200 OK

```json
[
  {
    "id": 1,
    "name": "강남도서관",
    "address": "서울특별시 강남구 ...",
    "latitude": 37.5172,
    "longitude": 127.0473,
    "phone": "02-1234-5678",
    "homepage": "https://example.go.kr",
    "updated_at": "2026-06-01T00:00:00Z"
  }
]
```

### `GET /api/v1/libraries/map-config/` — 200 OK

```json
{ "naver_map_client_id": "abc123" }
```

### `GET /api/v1/libraries/<pk>/` — 200 OK

```json
{
  "id": 1,
  "name": "강남도서관",
  "address": "서울특별시 강남구 ...",
  "latitude": 37.5172,
  "longitude": 127.0473,
  "phone": "02-1234-5678",
  "homepage": "https://example.go.kr",
  "updated_at": "2026-06-01T00:00:00Z"
}
```

---

## 에러 응답

| 상태 코드 | 발생 조건 | 응답 형식 |
|----------|----------|----------|
| 404 | `LibraryDetailView`: 해당 pk 없음 | `{"error": "해당 도서관을 찾을 수 없습니다."}` |
| 503 | `LibraryListView`: `SEOUL_API_KEY` 미설정 또는 API 호출 실패 | `{"error": "..."}` |
| 503 | `LibraryMapConfigView`: `NAVER_MAP_CLIENT_ID` 미설정 | `{"error": "NAVER_MAP_CLIENT_ID 환경변수가 설정되지 않았습니다."}` |

---

## 권한

모든 엔드포인트: `AllowAny` (인증 불필요)

---

## 구현 파일

- `libraries/services.py` — `fetch_libraries_from_api()`, `sync_libraries()`
- `libraries/serializers.py` — `LibrarySerializer`
- `libraries/views.py` — `LibraryListView`, `LibraryMapConfigView`, `LibraryDetailView`
- `libraries/urls.py` — URL 라우팅
- `libraries/tests.py` — 7개 테스트 (전체 PASS)
- `config/urls.py` — `/api/v1/libraries/` include 등록
- `.env.example` — `SEOUL_API_KEY=`, `NAVER_MAP_CLIENT_ID=` 추가

---

## 테스트 결과

| 테스트 | 결과 |
|-------|------|
| `test_list_from_db_cache` | PASS |
| `test_list_calls_api_when_no_cache` | PASS |
| `test_list_no_api_key` | PASS |
| `test_detail_success` | PASS |
| `test_detail_not_found` | PASS |
| `test_map_config_success` | PASS |
| `test_map_config_no_key` | PASS |
