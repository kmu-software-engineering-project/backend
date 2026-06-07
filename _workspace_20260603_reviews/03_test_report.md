# 테스트 결과 보고서 — reviews 앱

## 작성 일시
2026-06-03

---

## reviews 테스트 결과

### ReviewListCreateTests (14개)

| 테스트명 | 내용 | 결과 |
|---------|------|------|
| `test_list_filters_by_book_id` | book_id 필터링 시 해당 도서 리뷰만 반환 | PASS |
| `test_list_excludes_other_books` | 다른 book_id 리뷰가 응답에 포함되지 않음 | PASS |
| `test_list_missing_book_id_returns_400` | book_id 미전달 시 400 반환 | PASS |
| `test_list_ordering_latest` | ordering=latest 시 최신순 정렬 | PASS |
| `test_list_ordering_rating` | ordering=rating 시 평점 높은순 정렬 | PASS |
| `test_list_default_ordering_is_latest` | ordering 미전달 시 기본값 최신순 | PASS |
| `test_list_response_does_not_include_password` | 목록 응답에 password 필드 미포함 | PASS |
| `test_create_review_success` | 정상 입력 시 201 반환 및 닉네임·별점 확인 | PASS |
| `test_create_response_does_not_include_password` | 생성 응답에 password 필드 미포함 | PASS |
| `test_create_rating_below_minimum_returns_400` | 별점 0 입력 시 400 반환 | PASS |
| `test_create_rating_above_maximum_returns_400` | 별점 6 입력 시 400 반환 | PASS |
| `test_create_missing_nickname_returns_400` | nickname 누락 시 400 반환 | PASS |
| `test_create_missing_password_returns_400` | password 누락 시 400 반환 | PASS |
| `test_create_increments_review_count` | 리뷰 작성 후 DB 레코드 수 1 증가 | PASS |

### ReviewDeleteTests (4개)

| 테스트명 | 내용 | 결과 |
|---------|------|------|
| `test_delete_with_correct_password` | 올바른 비밀번호로 삭제 시 204 반환 및 DB 삭제 확인 | PASS |
| `test_delete_with_wrong_password_returns_400` | 틀린 비밀번호로 시 400 반환 및 리뷰 유지 확인 | PASS |
| `test_delete_nonexistent_review_returns_404` | 존재하지 않는 pk 삭제 시 404 반환 | PASS |
| `test_delete_without_password_returns_400` | password 미전달 시 400 반환 및 리뷰 유지 확인 | PASS |

**reviews 앱: 18/18 PASS**

---

## 전체 테스트 결과

| 앱 | 테스트 수 | 결과 |
|----|----------|------|
| reviews | 18 | PASS |

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

## 테스트 커버리지 요약

### ReviewListCreateView — `GET /api/v1/reviews/`
- `book_id` 필터링 정확성 (일치 도서만 반환, 타 도서 제외) 검증
- `book_id` 파라미터 누락 시 400 응답 검증
- `ordering=latest` / `ordering=rating` 정렬 방향 검증
- `ordering` 파라미터 미전달 시 기본값(최신순) 동작 검증
- 응답 본문에 `password` 필드 미포함 검증

### ReviewListCreateView — `POST /api/v1/reviews/`
- 정상 입력(전체 필드) 시 201 응답 및 반환 데이터 검증
- 생성 응답 본문에 `password` 필드 미포함 검증
- 별점 경계값(0, 6) 입력 시 400 응답 검증
- 필수 필드(`nickname`, `password`) 누락 시 400 응답 검증
- 작성 후 DB 레코드 수 증가 검증

### ReviewDeleteView — `DELETE /api/v1/reviews/{id}/`
- 올바른 비밀번호 입력 시 204 응답 및 DB에서 레코드 제거 검증
- 틀린 비밀번호 입력 시 400 응답 및 DB 레코드 유지 검증
- 존재하지 않는 pk 요청 시 404 응답 검증
- 비밀번호 미전달 시 400 응답 및 DB 레코드 유지 검증
