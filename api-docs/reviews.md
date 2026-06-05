# 리뷰 API

---

## GET /api/v1/reviews/

설명: 특정 도서의 리뷰 목록 조회
인증: 없음

### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `book_id` | string | ✅ | 도서 ISBN-13 |
| `ordering` | string | ❌ | 정렬 기준. `latest`(기본값) 또는 `rating` |

[Request]
```
GET /api/v1/reviews/?book_id=9788936434595&ordering=latest
```

[Response 200 OK]
```json
[
  {
    "id": 1,
    "bookId": "9788936434595",
    "bookTitle": "채식주의자",
    "nickname": "독자A",
    "rating": 5,
    "comment": "오래도록 마음에 남는 작품입니다.",
    "createdAt": "2026-06-03T12:00:00+09:00"
  },
  {
    "id": 2,
    "bookId": "9788936434595",
    "bookTitle": "채식주의자",
    "nickname": "책벌레",
    "rating": 4,
    "comment": "묵직한 여운이 있는 소설.",
    "createdAt": "2026-06-02T09:30:00+09:00"
  }
]
```

[Response 400 Bad Request]
```json
{
  "error": "book_id 파라미터가 필요합니다."
}
```

---

## POST /api/v1/reviews/

설명: 도서 리뷰 작성 (비밀번호 기반 익명 작성)
인증: 없음

### 요청 필드 설명

| 필드 | 타입 | 필수 | 제약 |
|------|------|------|------|
| `book_id` | string | ✅ | ISBN-13 |
| `book_title` | string | ✅ | 최대 500자 |
| `nickname` | string | ✅ | 최대 50자 |
| `password` | string | ✅ | 삭제 시 필요 (DB에 해시 저장) |
| `rating` | integer | ✅ | 1 ~ 5 |
| `comment` | string | ✅ | 최대 100자 |

[Request Body]
```json
{
  "book_id": "9788936434595",
  "book_title": "채식주의자",
  "nickname": "독자A",
  "password": "mypassword123",
  "rating": 5,
  "comment": "오래도록 마음에 남는 작품입니다."
}
```

[Response 201 Created]
```json
{
  "id": 1,
  "bookId": "9788936434595",
  "bookTitle": "채식주의자",
  "nickname": "독자A",
  "rating": 5,
  "comment": "오래도록 마음에 남는 작품입니다.",
  "createdAt": "2026-06-06T10:00:00+09:00"
}
```

[Response 400 Bad Request]
```json
{
  "rating": ["평점은 1에서 5 사이여야 합니다."],
  "comment": ["이 필드는 필수 항목입니다."]
}
```

---

## DELETE /api/v1/reviews/{id}/

설명: 작성 시 입력한 비밀번호로 본인 리뷰 삭제
인증: 없음 (비밀번호 검증)

### URL 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | integer | 삭제할 리뷰의 ID |

> **참고**: Swagger UI는 DELETE 요청 바디를 지원하지 않습니다. curl로 테스트하세요.
> ```bash
> curl -X DELETE http://localhost:8000/api/v1/reviews/1/ \
>   -H "Content-Type: application/json" \
>   -d '{"password": "mypassword123"}'
> ```

[Request Body]
```json
{
  "password": "mypassword123"
}
```

[Response 204 No Content]
```
(빈 응답)
```

[Response 400 Bad Request]
```json
{
  "error": "비밀번호가 일치하지 않습니다."
}
```

[Response 404 Not Found]
```json
{
  "detail": "찾을 수 없습니다."
}
```
