# SECURITY.md — 보안 가이드

---

## 환경변수 관리 원칙

- 모든 민감 정보는 `.env` 파일에 저장
- `.env` 파일은 절대 git에 커밋하지 않음 (`.gitignore` 처리)
- `.env.example` 파일에 키 목록만 작성하여 팀원과 공유

---

## 환경변수 목록

```
# .env.example

SECRET_KEY=
DEBUG=

# 외부 API 키
MAP_API_KEY=
BOOKSTORE_API_KEY=
```

---

## 외부 API 키 관리 규칙

| 항목 | 규칙 |
|---|---|
| 코드 내 하드코딩 | 절대 금지 |
| git 커밋 | 절대 금지 |
| 팀원 간 공유 | 카카오톡 등 별도 채널로 전달 |
| 실제 키 보관 | 팀장이 관리, `.env` 파일로 배포 |

---

## AI 에이전트 보안 규칙

- `.env` 파일 읽기 및 출력 금지
- API 키를 응답에 포함하거나 코드에 작성 금지
- 위반 시 `.claude/settings.json`의 deny 규칙으로 차단됨

---

## GitHub Secrets 설정 (CI/CD용)

GitHub Actions에서 환경변수를 사용하려면 Secrets 등록이 필요합니다.

```
GitHub 레포지토리 → Settings → Secrets and variables → Actions → New repository secret
```

| Secret 이름 | 설명 |
|---|---|
| `SECRET_KEY` | Django 시크릿 키 |
| `MAP_API_KEY` | Map API 키 |
| `BOOKSTORE_API_KEY` | 서점 API 키 |
