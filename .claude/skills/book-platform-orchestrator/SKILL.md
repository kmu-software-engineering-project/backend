---
name: book-platform-orchestrator
description: "도서 추천 플랫폼 백엔드 기능 개발을 에이전트 팀으로 조율하는 오케스트레이터. 새 Django 앱 개발, API 기능 추가, 기능 구현, 앱 스캐폴딩 요청 시 반드시 사용. 후속 작업: 기능 수정, 재구현, 업데이트, API 보완, 테스트 추가, 특정 앱만 다시, 이전 구현 개선, books/recommendations/reviews/bookstores/libraries 관련 모든 개발 요청 시 이 스킬을 사용."
---

# Book Platform Orchestrator

도서 추천 플랫폼 백엔드의 기능 개발을 에이전트 팀으로 조율하는 오케스트레이터.

## 실행 모드: 하이브리드

| Phase | 모드 | 이유 |
|-------|------|------|
| Phase 1 (분석) | 오케스트레이터 직접 | 단순 분석, 에이전트 불필요 |
| Phase 2 (설계+구현) | 에이전트 팀 | architect↔developer 실시간 협업 필요 |
| Phase 3 (테스트+품질) | 서브 에이전트 | 독립 검증, 팀 통신 불필요 |

## 에이전트 구성

| 팀원 | 에이전트 타입 | 역할 | 출력 |
|------|-------------|------|------|
| django-architect | django-architect | 앱 구조 + 모델 설계 | `_workspace/02_architect_models.md` |
| drf-developer | drf-developer | API 구현 | `_workspace/02_developer_api_list.md` |
| test-quality-engineer | test-quality-engineer | 테스트 + 품질 검사 | `_workspace/03_test_report.md` |

## 워크플로우

### Phase 0: 컨텍스트 확인

1. `_workspace/` 디렉토리 존재 여부 확인
2. 실행 모드 결정:
   - `_workspace/` 미존재 → **초기 실행**, Phase 1로 진행
   - `_workspace/` 존재 + 특정 부분 수정 요청 → **부분 재실행**, 해당 에이전트만 재호출하고 기존 산출물 유지
   - `_workspace/` 존재 + 새 기능 개발 요청 → **새 실행**, 기존 `_workspace/`를 `_workspace_{YYYYMMDD_HHMMSS}/`로 이동 후 Phase 1 진행

### Phase 1: 요구사항 분석

1. 사용자 요청에서 다음을 파악:
   - 개발 대상 앱 이름 (books, recommendations, reviews, bookstores, libraries)
   - 구현할 모델 및 필드
   - 구현할 API 엔드포인트 목록
   - 외부 API 연동 여부 (서점 API, 지도 API)
2. `_workspace/` 디렉토리 생성
3. 요구사항을 `_workspace/01_requirements.md`에 정리

### Phase 2: 설계 + 구현 (에이전트 팀)

**실행 모드:** 에이전트 팀

1. 팀 생성:
   ```
   TeamCreate(
     team_name: "book-dev-team",
     members: [
       {
         name: "django-architect",
         agent_type: "django-architect",
         model: "opus",
         prompt: "당신은 django-architect입니다. _workspace/01_requirements.md를 읽고 해당 Django 앱의 models.py를 설계 및 생성하세요. 앱이 없으면 'uv run python manage.py startapp {앱이름}'으로 생성하고 config/settings.py INSTALLED_APPS에 등록하세요. 모델 완성 후 'uv run python manage.py makemigrations {앱이름}'과 'uv run python manage.py migrate'를 실행하세요. 설계 요약을 _workspace/02_architect_models.md에 저장하고, SendMessage로 drf-developer에게 모델 구조를 알려주세요."
       },
       {
         name: "drf-developer",
         agent_type: "drf-developer",
         model: "opus",
         prompt: "당신은 drf-developer입니다. django-architect로부터 SendMessage를 수신하면 _workspace/02_architect_models.md를 읽고 serializers.py, views.py, urls.py를 구현하세요. 'config/urls.py'에 앱 URL을 include로 등록하고, 구현한 API 목록을 _workspace/02_developer_api_list.md에 저장하세요."
       }
     ]
   )
   ```

2. 작업 등록:
   ```
   TaskCreate(tasks: [
     {
       title: "앱 생성 및 모델 설계",
       description: "_workspace/01_requirements.md를 읽고 Django 앱 생성, 모델 설계, INSTALLED_APPS 등록",
       assignee: "django-architect"
     },
     {
       title: "마이그레이션 생성 및 적용",
       description: "makemigrations + migrate 실행",
       assignee: "django-architect",
       depends_on: ["앱 생성 및 모델 설계"]
     },
     {
       title: "API 구현",
       description: "django-architect SendMessage 수신 후 serializers.py, views.py, urls.py 구현",
       assignee: "drf-developer",
       depends_on: ["앱 생성 및 모델 설계"]
     },
     {
       title: "URL 등록",
       description: "config/urls.py에 앱 URL include 등록 및 _workspace/02_developer_api_list.md 작성",
       assignee: "drf-developer",
       depends_on: ["API 구현"]
     }
   ])
   ```

3. 팀원들이 자체 조율하며 작업 수행 (SendMessage로 협업)
4. 리더는 진행 상황을 TaskGet으로 주기적으로 확인하며, 막힌 팀원에게 SendMessage로 지시

### Phase 3: 테스트 + 품질 검사 (서브 에이전트)

**실행 모드:** 서브 에이전트

1. Phase 2 팀 정리:
   ```
   TeamDelete(team_name: "book-dev-team")
   ```

2. test-quality-engineer 서브 에이전트 실행:
   ```
   Agent(
     subagent_type: "test-quality-engineer",
     model: "opus",
     prompt: "_workspace/02_developer_api_list.md를 읽고 해당 API에 대한 {app}/tests.py를 작성하세요. 이후 다음 순서로 실행하세요: (1) uv run python manage.py migrate, (2) uv run python manage.py test, (3) uv run pre-commit run --all-files. 각 단계의 결과를 _workspace/03_test_report.md에 기록하세요. 테스트 실패 시 해당 파일을 수정하고 재실행하세요."
   )
   ```

### Phase 4: 정리 및 보고

1. `_workspace/03_test_report.md` 읽기
2. 사용자에게 결과 요약 보고:
   - 구현된 앱 및 API 목록
   - 테스트 결과 (Pass/Fail 수)
   - pre-commit 결과 (통과/실패 항목)
3. `_workspace/` 보존 (삭제 금지)
4. 개선 필요 사항이 있으면 사용자에게 피드백 요청

## 데이터 흐름

```
[오케스트레이터]
  → _workspace/01_requirements.md
  → TeamCreate → [django-architect] → models.py + migrate
                   │ SendMessage
                   ↓
                [drf-developer] → serializers.py + views.py + urls.py
                   │
                   ↓ _workspace/02_developer_api_list.md
  → TeamDelete
  → [test-quality-engineer 서브] → tests.py + test + pre-commit
                   ↓ _workspace/03_test_report.md
  → 결과 보고
```

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| django-architect 실패 | SendMessage로 재시도 요청, 재실패 시 오케스트레이터가 직접 모델 파일 생성 |
| drf-developer가 모델 수정 요청 | django-architect에게 SendMessage 중개, 마이그레이션 재실행 후 재개 |
| 테스트 실패 | `_workspace/03_test_report.md` 에러 분석 후 해당 파일 수정 및 재실행 |
| pre-commit 실패 (black/isort) | 자동 수정 후 재실행 |
| pre-commit 실패 (flake8) | 해당 라인 직접 수정 후 재실행 |
| 마이그레이션 충돌 | 기존 마이그레이션 파일 확인 후 의존성 수동 정의 |

## 테스트 시나리오

### 정상 흐름
1. 사용자: "books 앱 만들어줘. Book 모델에 제목, 저자, ISBN, 장르, 출판연도 필드 필요하고 목록/상세 API 구현해줘"
2. Phase 0: `_workspace/` 없음 → 초기 실행
3. Phase 1: 요구사항 분석 → `_workspace/01_requirements.md` 생성
4. Phase 2: 팀 구성 → architect가 Book 모델 생성+마이그레이션, developer가 BookSerializer+BookViewSet 구현
5. Phase 3: tests.py 작성 → 테스트 통과 → pre-commit 통과
6. Phase 4: "books 앱 구현 완료, API 2개(목록/상세), 테스트 4개 PASS" 보고

### 에러 흐름
1. Phase 3에서 테스트 실패 (`views.py`에서 필드명 오류 `titl` → `title`)
2. `_workspace/03_test_report.md`에서 에러 확인
3. `views.py` 수정 후 테스트 재실행
4. pre-commit 통과 후 완료 보고
