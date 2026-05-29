from rest_framework import serializers

# 선택지 상수 정의
FICTION_GENRES = [
    "romance",
    "fantasy",
    "sf",
    "mystery",
    "thriller",
    "horror",
    "historical",
    "coming_of_age",
    "family",
    "human_drama",
    "classic",
    "contemporary",
]
NONFICTION_GENRES = [
    "humanities",
    "psychology",
    "self_help",
    "economics",
    "social_political",
    "history",
    "science",
    "tech_it",
    "arts_culture",
    "travel",
    "health",
    "education",
    "religion",
]
INTEREST_CHOICES = [
    "relationships",
    "love",
    "growth",
    "comfort",
    "self_esteem",
    "psychology",
    "meaning_of_life",
    "money_investment",
    "career",
    "social_issues",
    "history",
    "science_tech",
    "arts_creation",
    "travel",
    "mystery",
    "new_world",
    "other",
]
PURPOSE_CHOICES = [
    "immersion",
    "mood_change",
    "comfort",
    "knowledge",
    "contemplation",
    "light_read",
    "deep_read",
    "assignment",
    "new_taste",
    "other",
]
MOOD_CHOICES = [
    "warm",
    "dark",
    "emotional",
    "cheerful",
    "calm",
    "philosophical",
    "tense",
    "realistic",
    "dreamy",
    "hopeful",
    "sad",
]
DIFFICULTY_CHOICES = [
    "very_easy",
    "moderate",
    "literary",
    "professional",
    "deep",
    "short_light",
    "long_ok",
]


class RecommendationRequestSerializer(serializers.Serializer):
    """사용자 취향 폼 입력을 검증하는 시리얼라이저."""

    # book_type: 필수, 단일 선택
    book_type = serializers.ChoiceField(choices=["FICTION", "NONFICTION"])

    # genres: 필수, 복수 선택 (ListField)
    genres = serializers.ListField(child=serializers.CharField(), min_length=1)

    # interests: 선택, 복수 선택
    interests = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    # interests_other: 선택, 자유 텍스트
    interests_other = serializers.CharField(
        required=False, allow_blank=True, default=""
    )

    # purpose: 선택, 복수 선택
    purpose = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    # purpose_other: 선택, 자유 텍스트
    purpose_other = serializers.CharField(required=False, allow_blank=True, default="")

    # mood: 선택, 복수 선택 (FICTION 전용)
    mood = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    # difficulty: 선택, 복수 선택
    difficulty = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    # favorite_books: 선택, 자유 텍스트
    favorite_books = serializers.CharField(required=False, allow_blank=True, default="")

    # avoid_elements: 선택, 자유 텍스트
    avoid_elements = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        book_type = attrs.get("book_type")
        genres = attrs.get("genres", [])
        interests = attrs.get("interests", []) or []
        interests_other = attrs.get("interests_other", "") or ""
        purpose = attrs.get("purpose", []) or []
        purpose_other = attrs.get("purpose_other", "") or ""
        mood = attrs.get("mood", []) or []
        difficulty = attrs.get("difficulty", []) or []

        # 1, 2. book_type에 따른 genres 유효성 검사
        if book_type == "FICTION":
            invalid_genres = [g for g in genres if g not in FICTION_GENRES]
            if invalid_genres:
                raise serializers.ValidationError(
                    {
                        "genres": (
                            f"FICTION에서 허용되지 않는 장르입니다: {invalid_genres}. "
                            f"허용 값: {FICTION_GENRES}"
                        )
                    }
                )
        elif book_type == "NONFICTION":
            invalid_genres = [g for g in genres if g not in NONFICTION_GENRES]
            if invalid_genres:
                raise serializers.ValidationError(
                    {
                        "genres": (
                            f"NONFICTION에서 허용되지 않는 장르입니다: {invalid_genres}. "
                            f"허용 값: {NONFICTION_GENRES}"
                        )
                    }
                )
            # 3. NONFICTION일 때 mood 값 무시
            attrs["mood"] = []
            mood = []

        # 4. interests에 "other" 포함 && interests_other가 빈 문자열이면 에러
        if "other" in interests and not interests_other.strip():
            raise serializers.ValidationError(
                {
                    "interests_other": (
                        "interests에 'other'가 포함된 경우 interests_other 값을 입력해야 합니다."
                    )
                }
            )

        # 5. purpose에 "other" 포함 && purpose_other가 빈 문자열이면 에러
        if "other" in purpose and not purpose_other.strip():
            raise serializers.ValidationError(
                {
                    "purpose_other": (
                        "purpose에 'other'가 포함된 경우 purpose_other 값을 입력해야 합니다."
                    )
                }
            )

        # 6. interests 각 항목이 INTEREST_CHOICES 안에 있어야 함
        invalid_interests = [i for i in interests if i not in INTEREST_CHOICES]
        if invalid_interests:
            raise serializers.ValidationError(
                {
                    "interests": (
                        f"허용되지 않는 관심사입니다: {invalid_interests}. "
                        f"허용 값: {INTEREST_CHOICES}"
                    )
                }
            )

        # 7. purpose 각 항목이 PURPOSE_CHOICES 안에 있어야 함
        invalid_purpose = [p for p in purpose if p not in PURPOSE_CHOICES]
        if invalid_purpose:
            raise serializers.ValidationError(
                {
                    "purpose": (
                        f"허용되지 않는 목적입니다: {invalid_purpose}. "
                        f"허용 값: {PURPOSE_CHOICES}"
                    )
                }
            )

        # 8. mood 각 항목이 MOOD_CHOICES 안에 있어야 함 (FICTION일 때만)
        if book_type == "FICTION":
            invalid_mood = [m for m in mood if m not in MOOD_CHOICES]
            if invalid_mood:
                raise serializers.ValidationError(
                    {
                        "mood": (
                            f"허용되지 않는 분위기입니다: {invalid_mood}. "
                            f"허용 값: {MOOD_CHOICES}"
                        )
                    }
                )

        # 9. difficulty 각 항목이 DIFFICULTY_CHOICES 안에 있어야 함
        invalid_difficulty = [d for d in difficulty if d not in DIFFICULTY_CHOICES]
        if invalid_difficulty:
            raise serializers.ValidationError(
                {
                    "difficulty": (
                        f"허용되지 않는 난이도입니다: {invalid_difficulty}. "
                        f"허용 값: {DIFFICULTY_CHOICES}"
                    )
                }
            )

        return attrs
