from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Library


def make_library(**kwargs):
    defaults = {
        "name": "테스트도서관",
        "address": "서울특별시 강남구 테스트로 1",
        "latitude": 37.5172,
        "longitude": 127.0473,
        "phone": "02-1234-5678",
        "homepage": "https://test.go.kr",
    }
    defaults.update(kwargs)
    return Library.objects.create(**defaults)


class LibraryListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_from_db_cache(self):
        """DB에 오늘 날짜 레코드 존재 → API 미호출, 200 반환"""
        make_library(name="강남도서관")
        with patch("libraries.services.fetch_libraries_from_api") as mock_fetch:
            response = self.client.get(reverse("library-list"))
        mock_fetch.assert_not_called()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_calls_api_when_no_cache(self):
        """DB 비어있음 → Seoul API mock 호출 → 200 반환"""
        mock_data = [
            {
                "name": "종로도서관",
                "address": "서울특별시 종로구 종로 1",
                "latitude": 37.5704,
                "longitude": 126.9928,
                "phone": "02-0000-0000",
                "homepage": "https://jongno.go.kr",
            }
        ]
        with patch(
            "libraries.services.fetch_libraries_from_api", return_value=mock_data
        ):
            response = self.client.get(reverse("library-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "종로도서관")

    def test_list_no_api_key(self):
        """SEOUL_API_KEY 없음 → 503"""
        with patch(
            "libraries.services.fetch_libraries_from_api",
            side_effect=ValueError("SEOUL_API_KEY 환경변수가 설정되지 않았습니다."),
        ):
            response = self.client.get(reverse("library-list"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)


class LibraryDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_detail_success(self):
        """존재하는 id → 200"""
        library = make_library(name="서초도서관")
        response = self.client.get(reverse("library-detail", kwargs={"pk": library.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "서초도서관")

    def test_detail_not_found(self):
        """존재하지 않는 id → 404"""
        response = self.client.get(reverse("library-detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)


class LibraryMapConfigViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_map_config_success(self):
        """KAKAO_MAP_API_KEY 설정됨 → 200, 키 반환"""
        with patch.dict("os.environ", {"KAKAO_MAP_API_KEY": "test_kakao_api_key"}):
            response = self.client.get(reverse("library-map-config"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["kakao_map_api_key"], "test_kakao_api_key")

    def test_map_config_no_key(self):
        """KAKAO_MAP_API_KEY 없음 → 503"""
        env_without_key = {
            k: v
            for k, v in __import__("os").environ.items()
            if k != "KAKAO_MAP_API_KEY"
        }
        with patch.dict("os.environ", env_without_key, clear=True):
            response = self.client.get(reverse("library-map-config"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)
