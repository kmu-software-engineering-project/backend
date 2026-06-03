from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """리뷰 목록 조회 및 생성 응답용 — 비밀번호 제외, camelCase."""

    bookId = serializers.CharField(source="book_id")
    bookTitle = serializers.CharField(source="book_title")
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "bookId",
            "bookTitle",
            "nickname",
            "rating",
            "comment",
            "createdAt",
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """리뷰 작성 입력용 — 비밀번호 포함(write_only), camelCase."""

    bookId = serializers.CharField(source="book_id")
    bookTitle = serializers.CharField(source="book_title")
    password = serializers.CharField(write_only=True, min_length=1)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "bookId",
            "bookTitle",
            "nickname",
            "password",
            "rating",
            "comment",
            "createdAt",
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class ReviewDeleteSerializer(serializers.Serializer):
    """리뷰 삭제 시 비밀번호 검증용."""

    password = serializers.CharField()

    def validate(self, attrs):
        review = self.context.get("review")
        if not check_password(attrs["password"], review.password):
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return attrs
