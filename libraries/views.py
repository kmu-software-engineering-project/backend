import os

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Library
from .serializers import LibrarySerializer
from .services import sync_libraries


class LibraryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="서울시 공공 도서관 목록",
        description=(
            "서울 열린데이터 광장 SeoulPublicLibraryInfo API를 통해 "
            "서울시 공공 도서관 전체 목록을 반환합니다. "
            "오늘 날짜 DB 캐시가 있으면 API를 호출하지 않고 DB 데이터를 반환합니다."
        ),
        responses={
            200: LibrarySerializer(many=True),
            503: {"description": "SEOUL_API_KEY 미설정 또는 API 호출 오류"},
        },
        examples=[
            OpenApiExample(
                "도서관 목록 응답 예시",
                value=[
                    {
                        "id": 1,
                        "name": "강남도서관",
                        "address": "서울특별시 강남구 ...",
                        "latitude": 37.5172,
                        "longitude": 127.0473,
                        "phone": "02-1234-5678",
                        "homepage": "https://example.go.kr",
                        "updated_at": "2026-06-01T00:00:00Z",
                    }
                ],
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        try:
            queryset = sync_libraries()
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            return Response(
                {"error": "도서관 데이터를 불러올 수 없습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = LibrarySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LibraryMapConfigView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 지도 API 키 조회",
        description=(
            "프론트엔드에서 카카오 지도를 초기화할 때 필요한 JavaScript API 키를 반환합니다."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "kakao_map_api_key": {
                        "type": "string",
                        "description": "카카오 지도 JavaScript API 키",
                    }
                },
            },
            503: {"description": "KAKAO_MAP_API_KEY 미설정"},
        },
        examples=[
            OpenApiExample(
                "지도 설정 응답 예시",
                value={"kakao_map_api_key": "abc123xyz"},
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        api_key = os.environ.get("KAKAO_MAP_API_KEY")
        if not api_key:
            return Response(
                {"error": "KAKAO_MAP_API_KEY 환경변수가 설정되지 않았습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"kakao_map_api_key": api_key},
            status=status.HTTP_200_OK,
        )


class LibraryDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="도서관 상세 정보",
        description="지정한 ID의 도서관 상세 정보를 반환합니다.",
        responses={
            200: LibrarySerializer,
            404: {"description": "해당 도서관을 찾을 수 없음"},
        },
    )
    def get(self, request, pk):
        try:
            library = Library.objects.get(pk=pk)
        except Library.DoesNotExist:
            return Response(
                {"error": "해당 도서관을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LibrarySerializer(library)
        return Response(serializer.data, status=status.HTTP_200_OK)
