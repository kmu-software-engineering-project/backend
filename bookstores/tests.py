from unittest.mock import MagicMock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

FAKE_NAVER_ENV = {
    "NAVER_CLIENT_ID": "test-client-id",
    "NAVER_CLIENT_SECRET": "test-client-secret",
}


class BookPriceAPITestCase(APITestCase):
    """BookPriceView API 테스트."""

    def setUp(self):
        self.url = reverse("book-prices")

    def _make_mock_response(self, items):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": items}
        mock_response.raise_for_status.return_value = None
        return mock_response

    def _make_book_item(
        self,
        title="채식주의자",
        discount="13500",
        isbn="9788936434595",
    ):
        return {
            "title": title,
            "author": "한강",
            "discount": discount,
            "isbn": isbn,
            "image": "https://bookthumb.phinf.naver.net/cover/test.jpg",
            "link": "https://search.shopping.naver.com/book/catalog/32482041666",
        }

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_prices_success(self, mock_get):
        """정상 응답: book 정보와 stores 링크가 반환되어야 한다."""
        mock_get.return_value = self._make_mock_response([self._make_book_item()])

        response = self.client.get(self.url, {"title": "채식주의자", "author": "한강"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = response.data["book"]
        self.assertEqual(book["title"], "채식주의자")
        self.assertEqual(book["naver_lowest_price"], 13500)
        self.assertEqual(book["naver_price_status"], "available")
        self.assertIsNotNone(book["naver_price_compare_url"])
        self.assertIsNotNone(book["isbn"])
        self.assertIsNotNone(book["cover_url"])
        self.assertGreater(len(response.data["stores"]), 0)

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_prices_unavailable(self, mock_get):
        """discount가 '0'이면 naver_price_status가 'unavailable'이어야 한다."""
        mock_get.return_value = self._make_mock_response(
            [self._make_book_item(discount="0")]
        )

        response = self.client.get(self.url, {"title": "절판된책"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = response.data["book"]
        self.assertIsNone(book["naver_lowest_price"])
        self.assertEqual(book["naver_price_status"], "unavailable")

    def test_prices_missing_title(self):
        """title 파라미터 누락 시 400을 반환해야 한다."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_prices_empty_result(self, mock_get):
        """검색 결과 없을 때 naver 가격은 None, stores는 링크만 반환해야 한다."""
        mock_get.return_value = self._make_mock_response([])

        response = self.client.get(self.url, {"title": "없는책제목"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = response.data["book"]
        self.assertIsNone(book["naver_lowest_price"])
        self.assertEqual(book["naver_price_status"], "unknown")
        self.assertIsNone(book["naver_price_compare_url"])
        self.assertGreater(len(response.data["stores"]), 0)

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_store_links_use_isbn(self, mock_get):
        """ISBN이 있으면 서점 링크가 ISBN을 포함해야 한다."""
        isbn = "9788936434595"
        mock_get.return_value = self._make_mock_response(
            [self._make_book_item(isbn=isbn)]
        )

        response = self.client.get(self.url, {"title": "채식주의자"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for store in response.data["stores"]:
            self.assertIn(isbn, store["purchase_url"])

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_author_sent_as_d_auth_not_mixed_in_query(self, mock_get):
        """제목+저자 검색 시 저자는 d_auth 파라미터로 분리하여 전달해야 한다."""
        mock_get.return_value = self._make_mock_response(
            [self._make_book_item(title="소년이 온다")]
        )

        self.client.get(self.url, {"title": "소년이 온다", "author": "한강"})

        call_params = mock_get.call_args[1]["params"]
        self.assertEqual(call_params["query"], "소년이 온다")
        self.assertEqual(call_params.get("d_auth"), "한강")
        self.assertNotIn("한강", call_params["query"])

    @patch.dict("os.environ", FAKE_NAVER_ENV)
    @patch("bookstores.services.requests.get")
    def test_isbn_mismatch_falls_back_to_title_search(self, mock_get):
        """ISBN 검색 결과 제목이 요청 제목과 다르면 제목+저자 검색으로 fallback해야 한다."""
        wrong_book = self._make_book_item(title="사피엔스", isbn="9788934972464")
        correct_book = self._make_book_item(title="호모 데우스", isbn="9788934977391")
        # 1차(ISBN) → 사피엔스 반환, 2차(제목) → 호모 데우스 반환
        mock_get.side_effect = [
            self._make_mock_response([wrong_book]),
            self._make_mock_response([correct_book]),
        ]

        response = self.client.get(
            self.url,
            {"title": "호모 데우스", "author": "유발 하라리", "isbn": "9788934972464"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = response.data["book"]
        self.assertEqual(book["isbn"], "9788934977391")
        for store in response.data["stores"]:
            self.assertNotIn("9788934972464", store["purchase_url"])

    @patch("bookstores.views.get_book_price_info")
    def test_prices_no_api_key(self, mock_fn):
        """네이버 API 키 미설정 시 503을 반환해야 한다."""
        mock_fn.side_effect = ValueError(
            "NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다."
        )

        response = self.client.get(self.url, {"title": "채식주의자"})

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
