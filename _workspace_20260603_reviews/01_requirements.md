# 요구사항 명세서 — reviews 앱

## 작업 개요

로그인 없이 닉네임·비밀번호 기반으로 도서 리뷰를 작성·조회·삭제하는 방명록형 `reviews` Django 앱을 신규 생성한다.
비밀번호는 DB에 해시 저장하며, 삭제 시 비밀번호를 검증해 본인 리뷰만 삭제할 수 있다.
프론트엔드 TypeScript 타입과의 일치를 위해 응답 필드명은 camelCase로 통일한다.

---

## 모델: `Review`

| 필드 | 타입 | 옵션 | 설명 |
|---|---|---|---|
| `book_id` | CharField(max_length=200) | db_index=True | 도서 ID (Kakao / Aladin ISBN13 등) |
| `book_title` | CharField(max_length=500) | — | 도서 제목 |
| `nickname` | CharField(max_length=50) | — | 작성자 닉네임 |
| `password` | CharField(max_length=128) | — | 비밀번호 (해시 저장) |
| `rating` | PositiveSmallIntegerField | MinValue(1), MaxValue(5) | 별점 1~5 |
| `comment` | CharField(max_length=100) | — | 한 줄 평 |
| `created_at` | DateTimeField | auto_now_add=True | 작성 시각 |

---

## API 엔드포인트

### 1. `GET /api/v1/reviews/`
- **목적**: 특정 도서의 리뷰 목록 조회
- **쿼리 파라미터**:
  - `book_id` (필수): 도서 ID
  - `ordering` (선택, 기본값 `latest`): `latest` = 최신순, `rating` = 평점 높은순
- **성공 응답 (200)**:
```json
[
  {
    "id": 1,
    "bookId": "9788936434120",
    "bookTitle": "채식주의자",
    "nickname": "독자A",
    "rating": 5,
    "comment": "훌륭한 작품",
    "createdAt": "2026-06-03T12:00:00+09:00"
  }
]
```
- **에러 응답**: 400 (`book_id` 파라미터 누락)
- **보안**: 응답에 `password` 필드 미포함

### 2. `POST /api/v1/reviews/`
- **목적**: 리뷰 작성
- **요청 body (camelCase)**:
```json
{
  "bookId": "9788936434120",
  "bookTitle": "채식주의자",
  "nickname": "독자A",
  "password": "mypassword",
  "rating": 5,
  "comment": "오래도록 마음에 남는 작품"
}
```
- **성공 응답 (201)**: 생성된 리뷰 객체 (`password` 미포함)
- **에러 응답**: 400 (필수 필드 누락, 별점 범위 오류)
- **보안**: 저장 시 `make_password()`로 해시 처리

### 3. `DELETE /api/v1/reviews/{id}/`
- **목적**: 본인 리뷰 삭제 (비밀번호 검증)
- **요청 body**:
```json
{ "password": "mypassword" }
```
- **성공 응답 (204)**: No Content
- **에러 응답**:
  - 400: 비밀번호 불일치 또는 누락
  - 404: 해당 리뷰 없음
- **보안**: `check_password()`로 해시 검증, 불일치 시 리뷰 유지

---

## 직렬화 구조

| Serializer | 용도 | 비밀번호 |
|---|---|---|
| `ReviewSerializer` | 목록 조회·생성 응답 | 미포함 |
| `ReviewCreateSerializer` | 리뷰 작성 입력 | write_only 포함 |
| `ReviewDeleteSerializer` | 삭제 비밀번호 검증 | 검증 후 폐기 |

---

## URL 구조

```
config/urls.py
└── /api/v1/reviews/  → reviews.urls
        ├── (list/create)  → ReviewListCreateView
        └── {id}/          → ReviewDeleteView
```

---

## 코드 스타일

- black (line-length 88)
- flake8
- isort
- pre-commit 훅 통과 필수
- 응답 필드명 camelCase 통일 (`bookId`, `bookTitle`, `createdAt`)

---

## 완료 조건

- [ ] `uv run python manage.py startapp reviews` 실행
- [ ] `config/settings.py` INSTALLED_APPS에 `"reviews"` 등록
- [ ] `Review` 모델 + 마이그레이션 완료
- [ ] `serializers.py`, `views.py`, `urls.py` 구현
- [ ] `config/urls.py`에 `/api/v1/reviews/` 등록
- [ ] 테스트 전체 PASS
- [ ] pre-commit 통과
