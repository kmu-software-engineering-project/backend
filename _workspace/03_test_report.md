# 테스트 및 품질 검사 보고서: recommendations 앱

## 1. 작업 개요

- 대상 앱: `recommendations`
- 담당: test-quality-engineer
- 입력 인계: `_workspace/02_developer_api_list.md` (drf-developer)
- 산출물: `recommendations/tests.py`

---

## 2. 테스트 결과 요약

| 항목 | 결과 |
|------|------|
| 실행 명령 | `uv run python manage.py test recommendations --verbosity=2` |
| 총 테스트 수 | **13** |
| PASS | **13** |
| FAIL | **0** |
| 실행 시간 | 0.078s |
| 종합 | **OK (전체 통과)** |

---

## 3. 테스트 상세 결과

### 3.1. Serializer 정상 입력 검증 (TestRecommendationRequestSerializerValid)

| 테스트명 | 결과 | 검증 항목 |
|----------|------|-----------|
| `test_valid_fiction_input` | PASS | FICTION + FICTION 장르 → `is_valid()` True |
| `test_valid_nonfiction_input` | PASS | NONFICTION + NONFICTION 장르 → `is_valid()` True |
| `test_nonfiction_mood_cleared` | PASS | NONFICTION 입력 시 mood가 `[]`로 덮어쓰임 |

### 3.2. Serializer 실패 입력 검증 (TestRecommendationRequestSerializerInvalid)

| 테스트명 | 결과 | 검증 항목 |
|----------|------|-----------|
| `test_fiction_with_nonfiction_genre` | PASS | FICTION + NONFICTION 장르 → ValidationError |
| `test_nonfiction_with_fiction_genre` | PASS | NONFICTION + FICTION 장르 → ValidationError |
| `test_interests_other_without_text` | PASS | `interests=['other']` + 빈 `interests_other` → 400 |
| `test_purpose_other_without_text` | PASS | `purpose=['other']` + 빈 `purpose_other` → 400 |
| `test_invalid_genre_value` | PASS | 존재하지 않는 장르 값 → ValidationError |
| `test_missing_book_type` | PASS | `book_type` 누락 → ValidationError |
| `test_empty_genres` | PASS | `genres` 빈 리스트 → ValidationError |

### 3.3. View 통합 테스트 (TestRecommendationView)

| 테스트명 | 결과 | 검증 항목 |
|----------|------|-----------|
| `test_post_valid_request_returns_200` | PASS | OpenAI mock 응답 → 200, `recommendations` 키 포함 |
| `test_post_invalid_request_returns_400` | PASS | 잘못된 입력 (FICTION + humanities) → 400 |
| `test_post_service_error_returns_503` | PASS | OpenAI mock에서 Exception → 503, `error` 키 포함 |

---

## 4. 모킹 전략

- `openai.OpenAI` 클래스 자체를 `unittest.mock.patch`로 패치하여 OpenAI 실제 API 호출 없이 테스트
- 패치 경로: `recommendations.services.openai.OpenAI`
- 성공 케이스: `chat.completions.create` 반환값을 `MagicMock`으로 구성하고 `choices[0].message.content`에 JSON 문자열 주입
- 실패 케이스: `chat.completions.create.side_effect = Exception(...)`로 예외 발생 시뮬레이션

---

## 5. pre-commit 결과

| 훅 | 결과 |
|----|------|
| black | **Passed** |
| isort | **Passed** |
| flake8 | **Passed** |
| trim trailing whitespace | **Passed** |
| fix end of files | **Passed** |
| check yaml | **Passed** |
| check for merge conflicts | **Passed** |
| detect private key | **Passed** |

실행 명령: `uv run pre-commit run --all-files`
종합 결과: **모든 훅 통과 (수정 불필요)**

---

## 6. 수정한 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `recommendations/tests.py` | 13개 테스트 신규 작성 (Serializer 10개 + View 3개) |

> 구현 파일(`serializers.py`, `services.py`, `views.py`)에 대한 추가 수정은 없었습니다. 모든 테스트가 한 번에 통과되었으며 pre-commit도 자동 수정 없이 통과되었습니다.

---

## 7. 품질 상태 종합

| 게이트 | 상태 |
|--------|------|
| Django 시스템 체크 | OK (0 issues) |
| 단위/통합 테스트 | OK (13/13 PASS) |
| 코드 포맷 (black) | OK |
| import 정렬 (isort) | OK |
| 코드 품질 (flake8) | OK |
| 파일 위생 (trailing-whitespace / EOF / yaml / merge-conflict / private-key) | OK |

**전체 결론: PASS** — `recommendations` 앱은 머지 가능한 품질 수준에 도달했습니다.

---

## 8. 산출물 위치

- `c:\Users\김석준\Desktop\se_backend\recommendations\tests.py`
- `c:\Users\김석준\Desktop\se_backend\_workspace\03_test_report.md` (본 문서)
