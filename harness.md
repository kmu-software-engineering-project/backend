# harness.md — AI 에이전트 하네스 구성 및 실행 방식

---

## 1. 하네스란?

이 프로젝트의 **하네스(Harness)**는 **AI 에이전트 팀이 Django 백엔드 기능을 자동으로 개발하는 파이프라인**입니다.
사람이 "이 앱 만들어줘"라고 요청하면, 여러 전문 에이전트가 역할을 나눠 설계 → 구현 → 테스트까지 자동으로 수행합니다.

---

## 2. 하네스 구성 요소

### A. 진입점: 스킬 3개 (`.claude/skills/`)

| 스킬 | 역할 | 트리거 |
|---|---|---|
| `book-platform-orchestrator` | 전체 파이프라인 조율 (오케스트레이터) | 앱 개발, API 구현 요청 시 |
| `django-app-scaffold` | 새 Django 앱 뼈대 생성 | `startapp`, 새 앱 추가 요청 시 |
| `drf-api-builder` | DRF API 패턴 가이드 | serializer / viewset / 외부 API 구현 시 |

### B. 전문 에이전트 3개 (`.claude/agents/`)

| 에이전트 | 역할 | 담당 산출물 |
|---|---|---|
| `django-architect` | 앱 구조·모델·마이그레이션 설계 | `models.py`, `_workspace_YYYYMMDD_앱이름/02_architect_models.md` |
| `drf-developer` | REST API 구현 | `serializers.py`, `views.py`, `urls.py`, `_workspace_YYYYMMDD_앱이름/02_developer_api_list.md` |
| `test-quality-engineer` | 테스트 작성 + 품질 검사 | `tests.py`, `_workspace_YYYYMMDD_앱이름/03_test_report.md` |

### C. 권한 설정 (`.claude/settings.json`)

에이전트가 실행할 수 있는 명령어가 명시적으로 통제됩니다.

**허용(allow)**

| 명령 | 용도 |
|---|---|
| `uv run`, `uv add`, `uv sync`, `uv lock` | 패키지 관리 및 서버 실행 |
| `python manage.py startapp / migrate / test / shell` | Django 앱 생성·DB·테스트 |
| `git status / diff / log / add / commit / checkout / branch` | 버전 관리 (읽기·로컬 커밋) |
| `black / flake8 / isort / pre-commit` | 코드 품질 검사 |

**금지(deny)**

| 명령 | 이유 |
|---|---|
| `git push` | 원격 반영은 사람이 직접 |
| `git reset --hard`, `git clean` | 작업 내용 파괴 위험 |
| `rm -rf` | 파일 일괄 삭제 위험 |
| `python manage.py flush / createsuperuser` | DB 초기화·계정 생성 위험 |
| `cat .env`, `echo .env` | 민감 정보 노출 방지 |

---

## 3. 하네스 실행 흐름 (4단계 파이프라인)

```
사용자 요청
    │
    ▼
[Phase 0] 컨텍스트 확인
  - _workspace_YYYYMMDD_앱이름/ 없음             → 초기 실행
  - _workspace_YYYYMMDD_앱이름/ 있음 + 새 기능  → 기존 폴더 보존, 새 _workspace_YYYYMMDD_앱이름/ 생성 후 재시작
  - _workspace_YYYYMMDD_앱이름/ 있음 + 수정 요청 → 해당 에이전트만 부분 재실행
    │
    ▼
[Phase 1] 오케스트레이터 직접 실행 — 요구사항 분석
  - 개발할 앱, 모델, API 엔드포인트 파악
  - _workspace/01_requirements.md 생성
    │
    ▼
[Phase 2] 에이전트 팀 협업 — 설계 + 구현
  ┌────────────────────────────────────┐
  │  TeamCreate("book-dev-team")       │
  │                                    │
  │  django-architect                  │
  │    ├ models.py 설계               │
  │    ├ makemigrations + migrate      │
  │    ├ 02_architect_models.md 작성  │
  │    └ SendMessage → drf-developer  │
  │               ↓                   │
  │  drf-developer                     │
  │    ├ serializers.py 구현          │
  │    ├ views.py 구현                │
  │    ├ urls.py 구현                 │
  │    └ 02_developer_api_list.md 작성│
  └────────────────────────────────────┘
    │
    ▼
[Phase 3] 서브 에이전트 — 테스트 + 품질 검사
  - TeamDelete("book-dev-team")
  - test-quality-engineer 단독 실행:
      (1) uv run python manage.py migrate
      (2) uv run python manage.py test
      (3) uv run pre-commit run --all-files  (black, isort, flake8)
  - 실패 시 자동 수정 후 재실행
  - 결과를 _workspace_YYYYMMDD_앱이름/03_test_report.md 에 기록
    │
    ▼
[Phase 4] 오케스트레이터 — 결과 보고
  - 구현 API 목록, 테스트 PASS/FAIL, pre-commit 결과 요약
  - _workspace_YYYYMMDD_앱이름/ 보존 (삭제 금지 — 작업 이력)
```

---

## 4. 에이전트 간 통신 방식

### 파일 기반 (`_workspace_YYYYMMDD_앱이름/` 공유 문서함)

```
_workspace_YYYYMMDD_앱이름/
├── 01_requirements.md        ← 오케스트레이터 작성  →  django-architect 읽음
├── 02_architect_models.md    ← django-architect 작성 →  drf-developer 읽음
├── 02_developer_api_list.md  ← drf-developer 작성   →  test-quality-engineer 읽음
└── 03_test_report.md         ← test-quality-engineer 작성 → 오케스트레이터 최종 확인
```

### 메시지 기반

- `SendMessage`: `django-architect` → `drf-developer` 로 모델 설계 완료 신호 실시간 전달
- 막힌 팀원에게 오케스트레이터가 `SendMessage`로 지시 및 재시도 요청

---

## 5. 에러 핸들링 전략

| 상황 | 대응 |
|---|---|
| `django-architect` 실패 | SendMessage로 재시도, 재실패 시 오케스트레이터가 직접 모델 파일 생성 |
| `drf-developer`가 모델 수정 요청 | `django-architect`에게 SendMessage 중개, 마이그레이션 재실행 후 재개 |
| 테스트 실패 | `03_test_report.md` 에러 분석 후 해당 파일 수정 및 재실행 |
| pre-commit 실패 (black/isort) | 자동 수정 후 재실행 |
| pre-commit 실패 (flake8) | 해당 라인 직접 수정 후 재실행 |
| 마이그레이션 충돌 | 기존 마이그레이션 파일 확인 후 의존성 수동 정의 |

---

## 6. 품질 게이트 (4-Stage Quality Gate)

```
[1. 코드 작성] → [2. PR 생성] → [3. 머지 후] → [4. Sprint 종료]
   로컬 검증       자동 검증    통합 환경 검증    수동 데모 검증
```

| 단계 | 시점 | 도구 | 기준 |
|---|---|---|---|
| 1단계 | 코드 작성 후 | pre-commit (black, isort, flake8, detect-private-key) | 오류 0건 |
| 2단계 | PR 생성 시 | GitHub Actions CI (`ci.yml`) | 린트 + 테스트 전부 통과 |
| 3단계 | develop 머지 후 | 수동 API 호출 + 프론트엔드 연동 확인 | 주요 엔드포인트 200 응답 |
| 4단계 | Sprint 종료 | 팀 데모 | Sprint 목표 기능 전체 동작 확인 |

**PR 머지 조건**

- CI 모든 단계 통과
- 팀원 1명 이상 코드 리뷰 승인
- 관련 테스트 코드 포함

---

## 7. 데이터 흐름 요약

```
[오케스트레이터]
  → _workspace_YYYYMMDD_앱이름/01_requirements.md
  → TeamCreate
        [django-architect] → models.py + migrate
              │ SendMessage
              ↓
        [drf-developer] → serializers.py + views.py + urls.py
              │
              ↓ _workspace_YYYYMMDD_앱이름/02_developer_api_list.md
  → TeamDelete
  → [test-quality-engineer] → tests.py + test + pre-commit
              │
              ↓ _workspace_YYYYMMDD_앱이름/03_test_report.md
  → 결과 보고
```

---

## 8. 현재 구현 앱 현황

| 앱 | 상태 | 담당 기능 |
|---|---|---|
| `recommendations` | 구현 완료 | GPT 기반 맞춤 도서 추천 |
| `reviews` | 구현 완료 | 평점·리뷰 작성 (방명록, 비밀번호 보호) |
| `libraries` | 구현 완료 | 서울시 도서관 위치 (서울 열린데이터 API) |
| `bookstores` | 구현 완료 | 온라인 서점 가격 비교 (네이버 도서 API) |
| `books` | 미구현 | 도서 정보, 장르별 탐색 (계획) |

**전체 테스트 현황 (최신 기준)**

| 앱 | 테스트 수 | 결과 |
|---|---|---|
| bookstores | 8 | PASS |
| libraries | 7 | PASS |
| recommendations | 14 | PASS |
| **합계** | **29** | **PASS** |
