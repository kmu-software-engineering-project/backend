# API 엔드포인트 목록 — reviews 앱

## 구현 완료 일시
2026-06-03

---

## 엔드포인트 목록

| # | URL | HTTP 메서드 | 뷰 클래스 | 설명 |
|---|-----|------------|----------|------|
| 1 | `/api/v1/reviews/` | GET | `ReviewListCreateView` | `book_id` 필터링 + `ordering` 정렬(latest/rating) |
| 2 | `/api/v1/reviews/` | POST | `ReviewListCreateView` | 닉네임·비밀번호·별점·한 줄 평 입력, 비밀번호 해시 저장 |
| 3 | `/api/v1/reviews/<int:pk>/` | DELETE | `ReviewDeleteView` | request body 비밀번호 검증 후 삭제 |

---

## 응답 형식

### `GET /api/v1/reviews/?book_id={id}&ordering=latest` — 200 OK

```json
[
  {
    "id": 2,
    "bookId": "9788936434120",
    "bookTitle": "채식주의자",
    "nickname": "독자B",
    "rating": 3,
    "comment": "평범했습니다",
    "createdAt": "2026-06-03T12:01:00+09:00"
  },
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

### `POST /api/v1/reviews/` — 201 Created

요청:
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

응답 (password 미포함):
```json
{
  "id": 1,
  "bookId": "9788936434120",
  "bookTitle": "채식주의자",
  "nickname": "독자A",
  "rating": 5,
  "comment": "오래도록 마음에 남는 작품",
  "createdAt": "2026-06-03T12:00:00+09:00"
}
```

### `DELETE /api/v1/reviews/{id}/` — 204 No Content

요청:
```json
{ "password": "mypassword" }
```

---

## 에러 응답

| 상태 코드 | 발생 조건 | 응답 형식 |
|----------|----------|----------|
| 400 | GET: `book_id` 파라미터 누락 | `{"error": "book_id 파라미터가 필요합니다."}` |
| 400 | POST: 필수 필드 누락 또는 별점 범위 초과(0 이하, 6 이상) | `{"field": ["에러 메시지"]}` |
| 400 | DELETE: 비밀번호 불일치 또는 누락 | `{"password": ["비밀번호가 일치하지 않습니다."]}` |
| 404 | DELETE: 해당 pk 없음 | `{"error": "해당 리뷰를 찾을 수 없습니다."}` |

---

## 권한

모든 엔드포인트: `AllowAny` (인증 불필요)

---

## 직렬화 구조

| Serializer | 사용처 | 특이사항 |
|---|---|---|
| `ReviewSerializer` | GET 응답, POST 응답 | password 미포함, camelCase 필드명 |
| `ReviewCreateSerializer` | POST 입력 | password write_only, create() 오버라이드로 make_password() 적용 |
| `ReviewDeleteSerializer` | DELETE 입력 | validate()에서 check_password() 검증, context로 review 객체 전달 |

---

## 구현 파일

- `reviews/models.py` — `Review` 모델
- `reviews/serializers.py` — `ReviewSerializer`, `ReviewCreateSerializer`, `ReviewDeleteSerializer`
- `reviews/views.py` — `ReviewListCreateView`, `ReviewDeleteView`
- `reviews/urls.py` — URL 라우팅
- `reviews/tests.py` — 18개 테스트
- `config/urls.py` — `/api/v1/reviews/` include 등록
