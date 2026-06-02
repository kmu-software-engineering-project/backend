# Developer API 구현 목록

## 수정된 API

### POST /api/v1/recommendations/
- recommendations/services.py의 GPT system_prompt 수정
- 응답에 isbn 필드 추가됨

## 신규 구현 API

### GET /api/v1/bookstores/prices/
- 파일: bookstores/views.py (BookPriceView)
- 서비스: bookstores/services.py (get_book_prices)
- 쿼리 파라미터: title(필수), author(선택), isbn(선택)
- 외부 API: 네이버 쇼핑 검색 API
- 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
- 응답: {"book": {...}, "stores": [...]}
