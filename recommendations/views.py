from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RecommendationRequestSerializer
from .services import get_book_recommendations


class RecommendationView(APIView):
    """사용자 취향 폼을 받아 GPT 기반 도서 5권을 추천한다."""

    permission_classes = [AllowAny]

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
