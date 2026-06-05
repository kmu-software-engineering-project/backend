# 도서 추천 플랫폼 API 명세서

## 개요

사용자 맞춤 도서 추천, 리뷰, 온라인 서점 가격 비교, 서울 공공도서관 위치 조회 기능을 제공하는 REST API입니다.

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1/`
- **응답 형식**: JSON
- **인증**: 없음 (전체 공개)
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI 스키마**: `http://localhost:8000/api/schema/`

---

## 엔드포인트 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/recommendations/` | GPT 기반 맞춤 도서 추천 |
| GET | `/api/v1/reviews/` | 도서 리뷰 목록 조회 |
| POST | `/api/v1/reviews/` | 도서 리뷰 작성 |
| DELETE | `/api/v1/reviews/{id}/` | 도서 리뷰 삭제 |
| GET | `/api/v1/libraries/` | 서울 공공도서관 목록 조회 |
| GET | `/api/v1/libraries/{id}/` | 공공도서관 상세 조회 |
| GET | `/api/v1/libraries/map-config/` | 카카오맵 API 키 조회 |
| GET | `/api/v1/bookstores/prices/` | 온라인 서점 가격 비교 |

---

## 상세 명세

- [도서 추천 API](./recommendations.md)
- [리뷰 API](./reviews.md)
- [도서관 API](./libraries.md)
- [서점 가격 비교 API](./bookstores.md)
