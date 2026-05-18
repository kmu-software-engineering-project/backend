# ADR-004: API 프레임워크로 Django REST Framework 채택

- **날짜:** 2025-05
- **상태:** 채택됨

## 결정

백엔드 API를 Django REST Framework(DRF)로 구현한다.

## 이유

- 백엔드 개발을 진행하는 팀원이 Python과 Django에 익숙하여 학습 비용이 낮다.
- DRF는 Serializer, ViewSet, Router 등 REST API 개발에 필요한 도구를 표준화된 방식으로 제공한다.
- ORM 기반 DB 접근, Admin 인터페이스, 마이그레이션 등 Django 생태계 전체를 활용할 수 있다.

## 고려했던 대안

| 대안 | 포기 이유 |
|---|---|
| FastAPI | 비동기 처리 장점이 있으나, 팀의 Django 경험을 살리기 어렵고 ORM 설정이 추가로 필요 |
| Flask | 경량 프레임워크이나 REST API 구조를 직접 설계해야 해 팀 규모 대비 오버헤드 발생 |

## 영향

- 모든 API는 `/api/v1/` prefix를 사용한다.
- 앱별 `serializers.py`, `views.py`, `urls.py` 구조를 표준으로 유지한다.
- 응답 형식은 항상 JSON이다.
