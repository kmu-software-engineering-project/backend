from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RecommendationRequestSerializer
from .services import get_book_recommendations


class RecommendationView(APIView):
    """사용자 취향 폼을 받아 GPT 기반 도서 5권을 추천한다."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="맞춤 도서 추천",
        description="사용자의 취향 정보를 입력받아 GPT 기반으로 도서 5권을 추천합니다.",
        request=RecommendationRequestSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "책 제목"},
                                "author": {"type": "string", "description": "저자"},
                                "reason": {
                                    "type": "string",
                                    "description": "추천 이유",
                                },
                                "isbn": {
                                    "type": "string",
                                    "nullable": True,
                                    "description": "ISBN-13",
                                },
                            },
                        },
                    }
                },
            }
        },
        examples=[
            OpenApiExample(
                "소설 추천 예시",
                value={
                    "book_type": "FICTION",
                    "genres": ["fantasy", "sf"],
                    "interests": ["new_world", "mystery"],
                    "purpose": ["immersion"],
                    "mood": ["tense", "dreamy"],
                    "difficulty": ["moderate"],
                    "favorite_books": "해리포터, 나니아 연대기",
                    "avoid_elements": "지나친 폭력",
                },
                request_only=True,
            ),
            OpenApiExample(
                "비문학 추천 예시",
                value={
                    "book_type": "NONFICTION",
                    "genres": ["science", "history"],
                    "interests": ["growth", "self_esteem"],
                    "purpose": ["knowledge", "contemplation"],
                    "difficulty": ["moderate", "deep"],
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            recommendations = get_book_recommendations(serializer.validated_data)
            return Response(
                {"recommendations": recommendations}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "추천 서비스 오류가 발생했습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
