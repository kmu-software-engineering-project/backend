# 도서 추천 API

---

## POST /api/v1/recommendations/

설명: 사용자 취향 정보를 기반으로 GPT-4o가 한국 출판 도서 5권을 추천
인증: 없음

### 요청 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `book_type` | string | ✅ | 도서 유형. `"FICTION"` 또는 `"NONFICTION"` |
| `genres` | string[] | ✅ | 장르 목록 (book_type에 따라 선택지 다름) |
| `interests` | string[] | ❌ | 관심사 목록 |
| `interests_other` | string | ❌ | interests에 `"other"` 포함 시 필수 |
| `purpose` | string[] | ❌ | 독서 목적 목록 |
| `purpose_other` | string | ❌ | purpose에 `"other"` 포함 시 필수 |
| `mood` | string[] | ❌ | 원하는 분위기 (FICTION 전용) |
| `difficulty` | string[] | ❌ | 난이도 선호 |
| `favorite_books` | string | ❌ | 좋아하는 책 자유 입력 |
| `avoid_elements` | string | ❌ | 기피 요소 자유 입력 |

### 선택지 목록

**genres (FICTION)**
`romance`, `fantasy`, `sf`, `mystery`, `thriller`, `horror`, `historical`, `coming_of_age`, `family`, `human_drama`, `classic`, `contemporary`

**genres (NONFICTION)**
`humanities`, `psychology`, `self_help`, `economics`, `social_political`, `history`, `science`, `tech_it`, `arts_culture`, `travel`, `health`, `education`, `religion`

**interests**
`relationships`, `love`, `growth`, `comfort`, `self_esteem`, `psychology`, `meaning_of_life`, `money_investment`, `career`, `social_issues`, `history`, `science_tech`, `arts_creation`, `travel`, `mystery`, `new_world`, `other`

**purpose**
`immersion`, `mood_change`, `comfort`, `knowledge`, `contemplation`, `light_read`, `deep_read`, `assignment`, `new_taste`, `other`

**mood** (FICTION 전용)
`warm`, `dark`, `emotional`, `cheerful`, `calm`, `philosophical`, `tense`, `realistic`, `dreamy`, `hopeful`, `sad`

**difficulty**
`very_easy`, `moderate`, `literary`, `professional`, `deep`, `short_light`, `long_ok`

---

[Request Body]
```json
{
  "book_type": "FICTION",
  "genres": ["fantasy", "sf"],
  "interests": ["new_world", "mystery"],
  "purpose": ["immersion", "deep_read"],
  "mood": ["tense", "dreamy"],
  "difficulty": ["moderate"],
  "favorite_books": "해리포터, 나니아 연대기",
  "avoid_elements": "지나친 폭력, 잔인한 묘사"
}
```

[Response 200 OK]
```json
{
  "recommendations": [
    {
      "title": "채식주의자",
      "author": "한강",
      "reason": "사용자가 선택한 '인간 드라마'와 '철학적' 분위기에 잘 맞는 작품입니다. 현실과 내면의 경계를 탐구하는 서사가 깊은 독서를 원하는 독자에게 적합합니다.",
      "isbn": "9788936434595"
    },
    {
      "title": "아몬드",
      "author": "손원평",
      "reason": "감정을 느끼지 못하는 주인공의 성장 이야기로, '성장'과 '인간 드라마' 관심사에 부합합니다.",
      "isbn": "9791190090162"
    }
  ]
}
```

[Response 400 Bad Request]
```json
{
  "book_type": ["이 필드는 필수 항목입니다."],
  "genres": ["FICTION 도서의 장르를 선택해주세요."]
}
```

[Response 503 Service Unavailable]
```json
{
  "error": "OPENAI_API_KEY가 설정되지 않았습니다."
}
```
