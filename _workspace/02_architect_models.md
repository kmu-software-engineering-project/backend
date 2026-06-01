# Architect 설계 요약

## Task 1: recommendations/services.py 수정
- system_prompt에 isbn 필드 추가 완료
- isbn: ISBN-13 13자리 숫자, 모를 경우 null

## Task 2: bookstores 앱 생성
- 앱 생성 완료: bookstores/
- INSTALLED_APPS 등록 완료
- DB 모델 없음 (외부 API 연동 전용 앱)

## 앱 구조
bookstores/
├── __init__.py
├── admin.py
├── apps.py
├── models.py      # 비어있음
├── tests.py
└── views.py       # drf-developer가 구현 예정

## drf-developer에게 전달사항
- bookstores 앱에는 모델 없음
- GET /api/v1/bookstores/prices/ 엔드포인트 구현 필요
- 네이버 쇼핑 API 연동 (services.py 신규 생성)
- 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
