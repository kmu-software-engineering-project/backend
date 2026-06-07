# 요구사항: 맞춤 도서 추천 기능 (recommendations 앱)

## 작업 개요
사용자 취향 폼 입력을 기반으로 OpenAI GPT API(gpt-4o)를 호출하여 맞춤 도서 5권을 추천하는 REST API 구현.

## 설계 결정 사항
| 항목 | 결정 |
|------|------|
| 앱 이름 | `recommendations` |
| 저장 방식 | Stateless (DB 저장 없음) |
| 인증 | 불필요 (AllowAny) |
| GPT 모델 | gpt-4o |
| 추천 권수 | 5권 |
| 엔드포인트 | POST /api/v1/recommendations/ |

## 구현 파일 목록
- `recommendations/models.py` - 빈 상태 유지 (Stateless)
- `recommendations/serializers.py` - 폼 입력 유효성 검사
- `recommendations/services.py` - OpenAI GPT 연동 서비스
- `recommendations/views.py` - RecommendationView (APIView)
- `recommendations/urls.py` - URL 라우팅
- `recommendations/tests.py` - 단위 테스트
- `config/urls.py` - 앱 URL 등록 (include)
- `config/settings.py` - INSTALLED_APPS 추가
- `.env.example` - OPENAI_API_KEY, OPENAI_MODEL 추가
- `pyproject.toml` - openai 패키지 의존성 추가

## 폼 필드 스펙

### 1. book_type (필수, 단일 선택)
| 값 | 표시명 |
|----|--------|
| `FICTION` | 소설/에세이/시·문학 |
| `NONFICTION` | 비문학 |

### 2. genres (필수, 복수 선택 - book_type 분기)

**FICTION 장르:**
| 값 | 표시명 |
|----|--------|
| `romance` | 로맨스 |
| `fantasy` | 판타지 |
| `sf` | SF |
| `mystery` | 추리/미스터리 |
| `thriller` | 스릴러 |
| `horror` | 공포 |
| `historical` | 역사소설 |
| `coming_of_age` | 성장소설 |
| `family` | 가족소설 |
| `human_drama` | 휴먼드라마 |
| `classic` | 고전문학 |
| `contemporary` | 현대문학 |

**NONFICTION 장르:**
| 값 | 표시명 |
|----|--------|
| `humanities` | 인문/철학 |
| `psychology` | 심리 |
| `self_help` | 자기계발 |
| `economics` | 경제/경영 |
| `social_political` | 사회/정치 |
| `history` | 역사 |
| `science` | 과학 |
| `tech_it` | 기술/IT |
| `arts_culture` | 예술/문화 |
| `travel` | 여행 |
| `health` | 건강 |
| `education` | 교육 |
| `religion` | 종교 |

### 3. interests (선택, 복수 선택 + 기타 자유 입력)
`relationships`, `love`, `growth`, `comfort`, `self_esteem`, `psychology`,
`meaning_of_life`, `money_investment`, `career`, `social_issues`, `history`,
`science_tech`, `arts_creation`, `travel`, `mystery`, `new_world`, `other`

- `interests_other`: 자유 텍스트 (interests에 "other" 포함 시 필수)

### 4. purpose (선택, 복수 선택 + 기타 자유 입력)
`immersion`, `mood_change`, `comfort`, `knowledge`, `contemplation`,
`light_read`, `deep_read`, `assignment`, `new_taste`, `other`

- `purpose_other`: 자유 텍스트 (purpose에 "other" 포함 시 필수)

### 5. mood (선택, 복수 선택 - FICTION 전용)
`warm`, `dark`, `emotional`, `cheerful`, `calm`, `philosophical`,
`tense`, `realistic`, `dreamy`, `hopeful`, `sad`

### 6. difficulty (선택, 복수 선택)
`very_easy`, `moderate`, `literary`, `professional`, `deep`, `short_light`, `long_ok`

### 7. favorite_books (선택, 자유 텍스트)
과거에 재밌게 읽었던 책 이름

### 8. avoid_elements (선택, 자유 텍스트)
피하고 싶은 요소

## Serializer 유효성 검사 규칙
1. `book_type=FICTION` → `genres`는 FICTION 장르 목록에서만 허용
2. `book_type=NONFICTION` → `genres`는 NONFICTION 장르 목록에서만 허용
3. `book_type=NONFICTION` → `mood` 필드 값 있어도 무시 (None으로 처리)
4. `interests`에 `other` 포함 시 → `interests_other` 필수
5. `purpose`에 `other` 포함 시 → `purpose_other` 필수

## API 요청/응답 스펙

### 요청 (POST /api/v1/recommendations/)
```json
{
  "book_type": "FICTION",
  "genres": ["romance", "contemporary"],
  "interests": ["love", "growth"],
  "purpose": ["immersion"],
  "mood": ["warm", "emotional"],
  "difficulty": ["moderate"],
  "favorite_books": "채식주의자, 82년생 김지영",
  "avoid_elements": "잔인한 묘사, 전쟁"
}
```

### 응답
```json
{
  "recommendations": [
    {
      "title": "책 제목",
      "author": "저자명",
      "reason": "추천 이유 (사용자 취향과의 연관성 설명)"
    }
  ]
}
```

## 환경변수
```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
```

## 테스트 시나리오
1. Serializer - 정상 FICTION 입력 검증
2. Serializer - 정상 NONFICTION 입력 검증
3. Serializer - FICTION 타입에 NONFICTION 장르 입력 시 에러
4. Serializer - interests에 other 포함 시 interests_other 없으면 에러
5. View - OpenAI mock으로 정상 추천 응답 확인
6. View - 잘못된 입력 시 400 반환 확인
