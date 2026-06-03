from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review
from .serializers import (
    ReviewCreateSerializer,
    ReviewDeleteSerializer,
    ReviewSerializer,
)


class ReviewListCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="리뷰 목록 조회",
        description="도서 ID로 해당 도서의 리뷰 목록을 조회합니다. ordering 파라미터로 정렬 기준을 선택할 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="book_id",
                type=str,
                required=True,
                description="도서 ID (Kakao/Aladin ISBN13 등)",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                enum=["latest", "rating"],
                default="latest",
                description="정렬 기준: latest(최신순), rating(평점 높은순)",
            ),
        ],
        responses={
            200: ReviewSerializer(many=True),
            400: {"description": "book_id 파라미터 누락"},
        },
        examples=[
            OpenApiExample(
                "최신순 응답 예시",
                value=[
                    {
                        "id": 2,
                        "book_id": "9788936434120",
                        "book_title": "채식주의자",
                        "nickname": "독자B",
                        "rating": 3,
                        "comment": "평범했습니다",
                        "created_at": "2026-06-03T12:01:00+09:00",
                    },
                    {
                        "id": 1,
                        "book_id": "9788936434120",
                        "book_title": "채식주의자",
                        "nickname": "독자A",
                        "rating": 5,
                        "comment": "훌륭한 작품",
                        "created_at": "2026-06-03T12:00:00+09:00",
                    },
                ],
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        book_id = request.query_params.get("book_id", "").strip()
        if not book_id:
            return Response(
                {"error": "book_id 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ordering = request.query_params.get("ordering", "latest")
        queryset = Review.objects.filter(book_id=book_id)
        if ordering == "rating":
            queryset = queryset.order_by("-rating", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="리뷰 작성",
        description="로그인 없이 닉네임·비밀번호·별점(1~5)·한 줄 평을 입력해 리뷰를 작성합니다.",
        request=ReviewCreateSerializer,
        responses={
            201: ReviewSerializer,
            400: {"description": "입력값 유효성 오류"},
        },
        examples=[
            OpenApiExample(
                "리뷰 작성 요청 예시",
                value={
                    "book_id": "9788936434120",
                    "book_title": "채식주의자",
                    "nickname": "독자A",
                    "password": "mypassword",
                    "rating": 5,
                    "comment": "오래도록 마음에 남는 작품",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ReviewDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="리뷰 삭제",
        description=(
            "작성 시 입력한 비밀번호를 request body로 전달해 본인 리뷰를 삭제합니다.\n\n"
            "**Swagger UI는 DELETE body를 렌더링하지 않으므로 curl 또는 Postman으로 테스트하세요.**\n\n"
            "```bash\n"
            "curl -X DELETE http://localhost:8000/api/v1/reviews/{id}/ \\\n"
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"password": "mypassword"}\'\n'
            "```"
        ),
        request=ReviewDeleteSerializer,
        responses={
            204: None,
            400: {"description": "비밀번호 불일치"},
            404: {"description": "리뷰 없음"},
        },
        examples=[
            OpenApiExample(
                "삭제 요청 예시",
                value={"password": "mypassword"},
                request_only=True,
            ),
        ],
    )
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(
                {"error": "해당 리뷰를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewDeleteSerializer(
            data=request.data, context={"review": review}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
