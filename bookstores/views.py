from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_book_price_info


class BookPriceView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="서점별 가격 비교",
        description=(
            "네이버 도서 검색 API를 통해 책의 네이버 최저가와 "
            "각 서점 구매 링크를 반환합니다."
        ),
        parameters=[
            OpenApiParameter(
                name="title",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="책 제목",
            ),
            OpenApiParameter(
                name="author",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="저자명 (검색 정확도 향상)",
            ),
            OpenApiParameter(
                name="isbn",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ISBN-13 (있으면 우선 사용)",
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "book": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                            "isbn": {"type": "string", "nullable": True},
                            "cover_url": {"type": "string", "nullable": True},
                            "naver_lowest_price": {
                                "type": "integer",
                                "nullable": True,
                                "description": (
                                    "네이버 기준 최저가 (원). "
                                    "unavailable/unknown이면 null"
                                ),
                            },
                            "naver_price_status": {
                                "type": "string",
                                "enum": ["available", "unavailable", "unknown"],
                                "description": (
                                    "available: 판매 중 | "
                                    "unavailable: 품절/절판 | "
                                    "unknown: 정보 없음"
                                ),
                            },
                            "naver_price_compare_url": {
                                "type": "string",
                                "nullable": True,
                                "description": "네이버 가격비교 페이지 URL",
                            },
                        },
                    },
                    "stores": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "store_name": {"type": "string"},
                                "price": {
                                    "type": "integer",
                                    "nullable": True,
                                    "description": "서점별 개별 가격 (현재 미지원, null)",
                                },
                                "purchase_url": {
                                    "type": "string",
                                    "description": "서점 구매/검색 페이지 URL",
                                },
                            },
                        },
                    },
                },
            },
            400: {"description": "title 파라미터 누락"},
            503: {"description": "네이버 API 키 미설정 또는 호출 오류"},
        },
        examples=[
            OpenApiExample(
                "채식주의자 가격 비교",
                value={
                    "title": "채식주의자",
                    "author": "한강",
                    "isbn": "9788936434595",
                },
                parameter_only=("title", "author", "isbn"),
            ),
        ],
    )
    def get(self, request):
        title = request.query_params.get("title", "").strip()

        if not title:
            return Response(
                {"error": "title 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author = request.query_params.get("author", "")
        isbn = request.query_params.get("isbn", "")

        try:
            result = get_book_price_info(title=title, author=author, isbn=isbn)
        except (ValueError, Exception):
            return Response(
                {"error": "가격 비교 서비스를 사용할 수 없습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(result, status=status.HTTP_200_OK)
