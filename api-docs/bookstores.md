# 서점 가격 비교 API

---

## GET /api/v1/bookstores/prices/

설명: 네이버 책 검색 API를 통해 도서 정보를 조회하고, 알라딘·교보문고·YES24·인터파크 4개 온라인 서점의 구매 링크와 네이버 최저가를 반환
인증: 없음

### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `title` | string | ✅ | 도서 제목 |
| `author` | string | ❌ | 저자명 (검색 정확도 향상) |
| `isbn` | string | ❌ | ISBN-13 (제공 시 우선 검색) |

### 가격 상태 (`naver_price_status`) 설명

| 값 | 설명 |
|----|------|
| `available` | 판매 중 |
| `unavailable` | 품절 또는 절판 (price = 0) |
| `unknown` | 가격 정보 없음 |

[Request]
```
GET /api/v1/bookstores/prices/?title=채식주의자&author=한강&isbn=9788936434595
```

[Response 200 OK]
```json
{
  "book": {
    "title": "채식주의자",
    "author": "한강",
    "isbn": "9788936434595",
    "cover_url": "https://bookthumb-phinf.pstatic.net/cover/068/235/06823506.jpg",
    "naver_lowest_price": 12600,
    "naver_price_status": "available",
    "naver_price_compare_url": "https://search.naver.com/search.naver?query=채식주의자+한강"
  },
  "stores": [
    {
      "store_name": "알라딘",
      "price": null,
      "purchase_url": "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchWord=채식주의자"
    },
    {
      "store_name": "교보문고",
      "price": null,
      "purchase_url": "https://search.kyobobook.co.kr/search?keyword=채식주의자"
    },
    {
      "store_name": "YES24",
      "price": null,
      "purchase_url": "https://www.yes24.com/Product/Search?query=채식주의자"
    },
    {
      "store_name": "인터파크",
      "price": null,
      "purchase_url": "https://book.interpark.com/search/bookSearch.do?query=채식주의자"
    }
  ]
}
```

[Response 400 Bad Request]
```json
{
  "error": "title 파라미터가 필요합니다."
}
```

[Response 503 Service Unavailable]
```json
{
  "error": "NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 설정되지 않았습니다."
}
```
