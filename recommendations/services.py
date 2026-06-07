import json
import os

import openai

# 한국어 변환 딕셔너리
BOOK_TYPE_KO = {
    "FICTION": "소설/에세이/시·문학",
    "NONFICTION": "비문학/실용/전문 도서",
}

GENRE_KO = {
    # FICTION
    "romance": "로맨스",
    "fantasy": "판타지",
    "sf": "SF",
    "mystery": "미스터리",
    "thriller": "스릴러",
    "horror": "공포",
    "historical": "역사 소설",
    "coming_of_age": "성장 소설",
    "family": "가족",
    "human_drama": "휴먼 드라마",
    "classic": "고전 문학",
    "contemporary": "현대 문학",
    # NONFICTION
    "humanities": "인문학",
    "psychology": "심리학",
    "self_help": "자기계발",
    "economics": "경제/경영",
    "social_political": "사회/정치",
    "history": "역사",
    "science": "과학",
    "tech_it": "기술/IT",
    "arts_culture": "예술/문화",
    "travel": "여행",
    "health": "건강",
    "education": "교육",
    "religion": "종교",
}

INTEREST_KO = {
    "relationships": "인간관계",
    "love": "사랑",
    "growth": "성장",
    "comfort": "위로",
    "self_esteem": "자존감",
    "psychology": "심리",
    "meaning_of_life": "삶의 의미",
    "money_investment": "돈/투자",
    "career": "커리어",
    "social_issues": "사회 이슈",
    "history": "역사",
    "science_tech": "과학/기술",
    "arts_creation": "예술/창작",
    "travel": "여행",
    "mystery": "미스터리",
    "new_world": "새로운 세계",
    "other": "기타",
}

PURPOSE_KO = {
    "immersion": "몰입",
    "mood_change": "기분 전환",
    "comfort": "위로",
    "knowledge": "지식 습득",
    "contemplation": "사색",
    "light_read": "가벼운 독서",
    "deep_read": "깊이 있는 독서",
    "assignment": "과제/학습",
    "new_taste": "새로운 취향 탐색",
    "other": "기타",
}

MOOD_KO = {
    "warm": "따뜻한",
    "dark": "어두운",
    "emotional": "감성적인",
    "cheerful": "유쾌한",
    "calm": "차분한",
    "philosophical": "철학적인",
    "tense": "긴장감 있는",
    "realistic": "현실적인",
    "dreamy": "몽환적인",
    "hopeful": "희망적인",
    "sad": "슬픈",
}

DIFFICULTY_KO = {
    "very_easy": "아주 쉬운",
    "moderate": "보통 난이도",
    "literary": "문학적인",
    "professional": "전문적인",
    "deep": "깊이 있는",
    "short_light": "짧고 가벼운",
    "long_ok": "길어도 괜찮음",
}


def _translate_list(values: list, mapping: dict) -> list:
    """코드 리스트를 한국어 리스트로 변환. 매핑이 없으면 원본 값을 그대로 사용."""
    return [mapping.get(v, v) for v in values or []]


def build_prompt(data: dict) -> str:
    """검증된 폼 데이터를 한국어 자연어 프롬프트로 변환한다."""
    book_type = data.get("book_type", "")
    genres = data.get("genres", []) or []
    interests = data.get("interests", []) or []
    interests_other = (data.get("interests_other") or "").strip()
    purpose = data.get("purpose", []) or []
    purpose_other = (data.get("purpose_other") or "").strip()
    mood = data.get("mood", []) or []
    difficulty = data.get("difficulty", []) or []
    favorite_books = (data.get("favorite_books") or "").strip()
    avoid_elements = (data.get("avoid_elements") or "").strip()

    book_type_ko = BOOK_TYPE_KO.get(book_type, book_type)
    genres_ko = _translate_list(genres, GENRE_KO)
    interests_ko = _translate_list(interests, INTEREST_KO)
    purpose_ko = _translate_list(purpose, PURPOSE_KO)
    mood_ko = _translate_list(mood, MOOD_KO)
    difficulty_ko = _translate_list(difficulty, DIFFICULTY_KO)

    lines = []
    lines.append(
        f"독자는 '{book_type_ko}' 분야를 선호하며, "
        f"세부 장르는 {', '.join(genres_ko)} 입니다."
    )

    if interests_ko:
        interests_text = ", ".join(interests_ko)
        if interests_other:
            interests_text += f" (기타 관심사: {interests_other})"
        lines.append(f"관심 있는 주제는 {interests_text} 입니다.")
    elif interests_other:
        lines.append(f"기타 관심 주제: {interests_other}.")

    if purpose_ko:
        purpose_text = ", ".join(purpose_ko)
        if purpose_other:
            purpose_text += f" (기타 목적: {purpose_other})"
        lines.append(f"독서를 통해 얻고 싶은 것은 {purpose_text} 입니다.")
    elif purpose_other:
        lines.append(f"기타 독서 목적: {purpose_other}.")

    if book_type == "FICTION" and mood_ko:
        lines.append(f"선호하는 작품 분위기는 {', '.join(mood_ko)} 입니다.")

    if difficulty_ko:
        lines.append(f"선호하는 책의 깊이/난이도는 {', '.join(difficulty_ko)} 입니다.")

    if favorite_books:
        lines.append(f"좋아하는 책/작가/작품: {favorite_books}.")

    if avoid_elements:
        lines.append(f"피하고 싶은 요소: {avoid_elements}.")

    lines.append(
        "위 취향을 종합적으로 고려하여 한국 독자에게 적합한 책 5권을 추천해 주세요. "
        "단, 5권이 장르·분위기·작가·출판 시기 면에서 서로 겹치지 않도록 다양하게 구성해 주세요. "
        "유명한 책과 덜 알려진 작품을 균형 있게 포함해 주세요."
    )

    return "\n".join(lines)


def get_book_recommendations(validated_data: dict) -> list:
    """
    OpenAI GPT API를 호출하여 맞춤 도서 5권을 추천합니다.
    반환: [{"title": str, "author": str, "reason": str}, ...]
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    user_prompt = build_prompt(validated_data)

    system_prompt = """당신은 도서 전문가이자 큐레이터입니다. 사용자의 취향 정보를 바탕으로 독자에게 적합한 책 5권을 추천해주세요.

반드시 다음 JSON 형식으로만 응답하세요:
{
  "recommendations": [
    {"title": "책 제목", "author": "저자명", "reason": "추천 이유 (사용자 취향과의 연관성)",
     "isbn": "한국어판 ISBN-13 숫자 13자리 또는 null"}
  ]
}

[출판 조건]
- 반드시 한국에서 출판된 국내 도서 또는 한국어로 번역 출판된 도서만 추천
- 번역서는 반드시 한국어 번역 제목과 번역서 저자명(역자 제외)을 사용
- 영어 원서 등 외국어 원본 도서는 추천하지 않음
- isbn은 한국어판 ISBN-13 번호 (9788 또는 9791로 시작하는 13자리 숫자). 확실하지 않으면 null

[다양성 규칙 — 반드시 준수]
- 동일 저자의 책을 2권 이상 추천하지 않음
- 5권 중 최소 2권은 대중적으로 덜 알려진 작품(숨겨진 명작, 주목받지 못한 도서)을 포함할 것
- 출판 시기를 다양하게 구성할 것 (최신작·스테디셀러·고전 중 최소 2가지 이상 혼합)
- 한국 작가 도서와 번역서를 적절히 혼합할 것 (한쪽으로만 치우치지 않음)
- 각 책은 사용자 취향의 서로 다른 측면(장르·분위기·주제·문체·독서 목적 등)을 주로 반영하여 선택할 것
  예: 1권은 분위기 중심, 2권은 주제 중심, 3권은 문체 중심으로 각각 다른 이유로 선정

[추천 이유 작성 기준]
- reason은 이 독자에게 이 책이 왜 적합한지에 초점을 맞춰 2-3문장으로 구체적으로 작성
- 각 책의 reason은 사용자 취향 중 서로 다른 요소를 중심으로 작성 (5권이 비슷한 이유로 반복되지 않게)
- 단순 줄거리 요약이 아닌, 해당 독자의 취향·목적·분위기 선호와 연결하여 작성"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.9,
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("recommendations", [])
