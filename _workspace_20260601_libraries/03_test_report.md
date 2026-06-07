# 테스트 결과 보고서 — libraries 앱

## 작성 일시
2026-06-01

---

## libraries 테스트 결과

| 테스트명 | 클래스 | 결과 |
|---------|--------|------|
| `test_list_from_db_cache` | `LibraryListViewTest` | PASS |
| `test_list_calls_api_when_no_cache` | `LibraryListViewTest` | PASS |
| `test_list_no_api_key` | `LibraryListViewTest` | PASS |
| `test_detail_success` | `LibraryDetailViewTest` | PASS |
| `test_detail_not_found` | `LibraryDetailViewTest` | PASS |
| `test_map_config_success` | `LibraryMapConfigViewTest` | PASS |
| `test_map_config_no_key` | `LibraryMapConfigViewTest` | PASS |

**libraries 앱: 7/7 PASS**

---

## 전체 테스트 결과

| 앱 | 테스트 수 | 결과 |
|----|----------|------|
| bookstores | 8 | PASS |
| libraries | 7 | PASS |
| recommendations | 14 | PASS |
| **합계** | **29** | **PASS** |

```
Ran 29 tests in 0.317s
OK
```

---

## pre-commit 결과

| 훅 | 결과 |
|----|------|
| black | Passed |
| isort | Passed |
| flake8 | Passed |
| trim trailing whitespace | Passed |
| fix end of files | Passed |
| check yaml | Passed |
| check for merge conflicts | Passed |
| detect private key | Passed |

**모든 pre-commit 훅 통과**

---

## 수정 사항

없음. 기존 구현 및 테스트 코드가 모두 정상 동작함을 확인.

---

## 테스트 커버리지 요약

### LibraryListView (`GET /api/v1/libraries/`)
- DB 캐시 히트 시 Seoul API 미호출 검증
- DB 미캐시 시 API 호출 및 데이터 저장 검증
- API 키 미설정 시 503 반환 검증

### LibraryDetailView (`GET /api/v1/libraries/<pk>/`)
- 존재하는 pk에 대한 200 응답 및 데이터 검증
- 없는 pk에 대한 404 응답 검증

### LibraryMapConfigView (`GET /api/v1/libraries/map-config/`)
- NAVER_MAP_CLIENT_ID 설정 시 200 응답 및 키 값 포함 검증
- NAVER_MAP_CLIENT_ID 미설정 시 503 반환 검증
