from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Review


class ReviewListCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("review-list-create")
        self.book_id = "9788936434120"
        self.review_a = Review.objects.create(
            book_id=self.book_id,
            book_title="채식주의자",
            nickname="독자A",
            password=make_password("pw1"),
            rating=5,
            comment="훌륭한 작품",
        )
        self.review_b = Review.objects.create(
            book_id=self.book_id,
            book_title="채식주의자",
            nickname="독자B",
            password=make_password("pw2"),
            rating=3,
            comment="평범했습니다",
        )
        Review.objects.create(
            book_id="other_book_id",
            book_title="다른 책",
            nickname="독자C",
            password=make_password("pw3"),
            rating=4,
            comment="다른 책 리뷰",
        )

    # ── 목록 조회 ──────────────────────────────────────────────────────

    def test_list_filters_by_book_id(self):
        response = self.client.get(self.url, {"book_id": self.book_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_excludes_other_books(self):
        response = self.client.get(self.url, {"book_id": self.book_id})
        book_ids = [r["bookId"] for r in response.data]
        self.assertTrue(all(b == self.book_id for b in book_ids))

    def test_list_missing_book_id_returns_400(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_ordering_latest(self):
        response = self.client.get(
            self.url, {"book_id": self.book_id, "ordering": "latest"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_ats = [r["createdAt"] for r in response.data]
        self.assertEqual(created_ats, sorted(created_ats, reverse=True))

    def test_list_ordering_rating(self):
        response = self.client.get(
            self.url, {"book_id": self.book_id, "ordering": "rating"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_list_default_ordering_is_latest(self):
        """ordering 파라미터 미전달 시 기본값은 최신순."""
        response = self.client.get(self.url, {"book_id": self.book_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_ats = [r["createdAt"] for r in response.data]
        self.assertEqual(created_ats, sorted(created_ats, reverse=True))

    def test_list_response_does_not_include_password(self):
        response = self.client.get(self.url, {"book_id": self.book_id})
        for review in response.data:
            self.assertNotIn("password", review)

    # ── 리뷰 작성 ──────────────────────────────────────────────────────

    def test_create_review_success(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자D",
            "password": "secret",
            "rating": 4,
            "comment": "인상 깊었습니다",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nickname"], "독자D")
        self.assertEqual(response.data["rating"], 4)

    def test_create_response_does_not_include_password(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자E",
            "password": "mypassword",
            "rating": 5,
            "comment": "완벽",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

    def test_create_rating_below_minimum_returns_400(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자F",
            "password": "pw",
            "rating": 0,
            "comment": "별점 오류",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating_above_maximum_returns_400(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자G",
            "password": "pw",
            "rating": 6,
            "comment": "별점 오류",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_nickname_returns_400(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "password": "pw",
            "rating": 3,
            "comment": "닉네임 없음",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_password_returns_400(self):
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자H",
            "rating": 3,
            "comment": "비밀번호 없음",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_increments_review_count(self):
        before = Review.objects.filter(book_id=self.book_id).count()
        payload = {
            "bookId": self.book_id,
            "bookTitle": "채식주의자",
            "nickname": "독자I",
            "password": "pw",
            "rating": 2,
            "comment": "별로였어요",
        }
        self.client.post(self.url, payload, format="json")
        after = Review.objects.filter(book_id=self.book_id).count()
        self.assertEqual(after, before + 1)


class ReviewDeleteTests(APITestCase):
    def setUp(self):
        self.review = Review.objects.create(
            book_id="9788936434120",
            book_title="채식주의자",
            nickname="독자A",
            password=make_password("correctpw"),
            rating=5,
            comment="좋았습니다",
        )
        self.url = reverse("review-delete", kwargs={"pk": self.review.pk})

    def test_delete_with_correct_password(self):
        response = self.client.delete(
            self.url, {"password": "correctpw"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_with_wrong_password_returns_400(self):
        response = self.client.delete(self.url, {"password": "wrongpw"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_nonexistent_review_returns_404(self):
        url = reverse("review-delete", kwargs={"pk": 99999})
        response = self.client.delete(url, {"password": "correctpw"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_without_password_returns_400(self):
        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())
