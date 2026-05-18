# ADR-002: 개발 DB는 SQLite, 운영 DB는 PostgreSQL 전환 예정

- **날짜:** 2025-05
- **상태:** 채택됨

## 결정

개발 환경에서는 SQLite를 사용하고, 운영 배포 시 PostgreSQL로 전환한다.

## 이유

- SQLite는 설치와 설정이 필요 없어 팀원 전원이 별도 DB 서버 없이 즉시 개발을 시작할 수 있다.
- 이 프로젝트의 개발 기간이 짧고 팀 규모가 작아, 초기에 DB 인프라에 드는 비용을 최소화하는 것이 우선이다.
- Django ORM을 사용하므로 SQLite → PostgreSQL 전환 시 코드 변경은 `settings.py`의 `DATABASES` 설정 하나로 충분하다.

## 고려했던 대안

| 대안 | 포기 이유 |
|---|---|
| 처음부터 PostgreSQL | 팀원마다 DB 서버 설치/설정 필요, 초기 진입 장벽 높음 |
| MySQL | PostgreSQL 대비 Django와의 호환성 및 JSON 지원이 약함 |

## 운영 전환 시 할 일

1. `pyproject.toml`에 `psycopg2` 또는 `psycopg` 추가
2. `settings.py`의 `DATABASES` 설정을 환경변수 기반으로 교체
3. AWS RDS 또는 컨테이너 DB 연결 설정
