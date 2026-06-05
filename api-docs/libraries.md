# 도서관 API

---

## GET /api/v1/libraries/

설명: 서울 공공도서관 전체 목록 조회. 당일 데이터가 DB에 있으면 캐시 반환, 없으면 서울 열린데이터 광장 API를 호출하여 동기화 후 반환
인증: 없음

[Request]
```
GET /api/v1/libraries/
```

[Response 200 OK]
```json
[
  {
    "id": 1,
    "name": "강남도서관",
    "address": "서울특별시 강남구 삼성로 212",
    "latitude": 37.5172,
    "longitude": 127.0473,
    "phone": "02-3463-7460",
    "homepage": "https://www.gangnampubliclibrary.go.kr",
    "updated_at": "2026-06-06T00:00:00Z"
  },
  {
    "id": 2,
    "name": "서초도서관",
    "address": "서울특별시 서초구 서초중앙로 96",
    "latitude": 37.4837,
    "longitude": 127.0324,
    "phone": "02-2155-8330",
    "homepage": "https://lib.seocho.go.kr",
    "updated_at": "2026-06-06T00:00:00Z"
  }
]
```

[Response 503 Service Unavailable]
```json
{
  "error": "SEOUL_API_KEY가 설정되지 않았습니다."
}
```

---

## GET /api/v1/libraries/{id}/

설명: 특정 공공도서관 상세 정보 조회
인증: 없음

### URL 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | integer | 도서관 ID |

[Request]
```
GET /api/v1/libraries/1/
```

[Response 200 OK]
```json
{
  "id": 1,
  "name": "강남도서관",
  "address": "서울특별시 강남구 삼성로 212",
  "latitude": 37.5172,
  "longitude": 127.0473,
  "phone": "02-3463-7460",
  "homepage": "https://www.gangnampubliclibrary.go.kr",
  "updated_at": "2026-06-06T00:00:00Z"
}
```

[Response 404 Not Found]
```json
{
  "detail": "찾을 수 없습니다."
}
```

---

## GET /api/v1/libraries/map-config/

설명: 프론트엔드에서 카카오맵을 초기화할 때 필요한 JavaScript API 키 반환
인증: 없음

[Request]
```
GET /api/v1/libraries/map-config/
```

[Response 200 OK]
```json
{
  "kakao_map_api_key": "abc123xyz..."
}
```

[Response 503 Service Unavailable]
```json
{
  "error": "KAKAO_MAP_API_KEY가 설정되지 않았습니다."
}
```
