import json
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from recommendations.serializers import RecommendationRequestSerializer


class TestRecommendationRequestSerializerValid(TestCase):
    """RecommendationRequestSerializer 정상 입력 검증 테스트."""

    def test_valid_fiction_input(self):
        """FICTION + FICTION 장르 조합은 유효해야 한다."""
        data = {
            "book_type": "FICTION",
            "genres": ["romance", "contemporary"],
            "interests": ["love", "growth"],
            "purpose": ["immersion", "comfort"],
            "mood": ["warm", "emotional"],
            "difficulty": ["moderate", "short_light"],
            "favorite_books": "정세랑 - 보건교사 안은영",
            "avoid_elements": "잔혹한 묘사",
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_nonfiction_input(self):
        """NONFICTION + NONFICTION 장르 조합은 유효해야 한다."""
        data = {
            "book_type": "NONFICTION",
            "genres": ["psychology", "self_help"],
            "interests": ["self_esteem"],
            "purpose": ["knowledge"],
            "difficulty": ["moderate"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nonfiction_mood_cleared(self):
        """NONFICTION 입력에 mood가 포함되어도 validated_data에서 []로 변경되어야 한다."""
        data = {
            "book_type": "NONFICTION",
            "genres": ["history", "humanities"],
            "mood": ["warm", "emotional"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data.get("mood"), [])


class TestRecommendationRequestSerializerInvalid(TestCase):
    """RecommendationRequestSerializer 잘못된 입력 검증 테스트."""

    def test_fiction_with_nonfiction_genre(self):
        """FICTION + NONFICTION 장르 조합은 ValidationError를 발생시켜야 한다."""
        data = {
            "book_type": "FICTION",
            "genres": ["humanities"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("genres", serializer.errors)

    def test_nonfiction_with_fiction_genre(self):
        """NONFICTION + FICTION 장르 조합은 ValidationError를 발생시켜야 한다."""
        data = {
            "book_type": "NONFICTION",
            "genres": ["romance"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("genres", serializer.errors)

    def test_interests_other_without_text(self):
        """interests에 'other' 포함 + interests_other 빈 문자열이면 에러."""
        data = {
            "book_type": "FICTION",
            "genres": ["romance"],
            "interests": ["love", "other"],
            "interests_other": "",
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("interests_other", serializer.errors)

    def test_purpose_other_without_text(self):
        """purpose에 'other' 포함 + purpose_other 빈 문자열이면 에러."""
        data = {
            "book_type": "FICTION",
            "genres": ["romance"],
            "purpose": ["immersion", "other"],
            "purpose_other": "",
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("purpose_other", serializer.errors)

    def test_invalid_genre_value(self):
        """존재하지 않는 장르 값은 ValidationError를 발생시켜야 한다."""
        data = {
            "book_type": "FICTION",
            "genres": ["nonexistent_genre"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("genres", serializer.errors)

    def test_missing_book_type(self):
        """book_type이 없으면 ValidationError를 발생시켜야 한다."""
        data = {
            "genres": ["romance"],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("book_type", serializer.errors)

    def test_empty_genres(self):
        """genres가 빈 리스트면 ValidationError를 발생시켜야 한다."""
        data = {
            "book_type": "FICTION",
            "genres": [],
        }
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("genres", serializer.errors)


class TestRecommendationView(APITestCase):
    """RecommendationView API 테스트."""

    def setUp(self):
        self.url = reverse("recommendation")
        self.valid_payload = {
            "book_type": "FICTION",
            "genres": ["romance", "contemporary"],
            "interests": ["love", "growth"],
            "purpose": ["immersion", "comfort"],
            "mood": ["warm", "emotional"],
            "difficulty": ["moderate", "short_light"],
            "favorite_books": "정세랑 - 보건교사 안은영",
            "avoid_elements": "잔혹한 묘사",
        }

    @patch("recommendations.services.openai.OpenAI")
    def test_post_valid_request_returns_200(self, mock_openai_class):
        """정상 FICTION 입력 + OpenAI mock → 200, recommendations 키가 있어야 한다."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "recommendations": [
                    {
                        "title": "채식주의자",
                        "author": "한강",
                        "reason": "테스트 이유",
                    }
                ]
            }
        )
        mock_client.chat.completions.create.return_value = mock_response

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendations", response.data)
        self.assertEqual(len(response.data["recommendations"]), 1)
        self.assertEqual(response.data["recommendations"][0]["title"], "채식주의자")

    def test_post_invalid_request_returns_400(self):
        """잘못된 입력은 400을 반환해야 한다."""
        invalid_payload = {
            "book_type": "FICTION",
            "genres": ["humanities"],  # NONFICTION 전용 장르
        }
        response = self.client.post(self.url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("recommendations.services.openai.OpenAI")
    def test_post_service_error_returns_503(self, mock_openai_class):
        """OpenAI mock에서 Exception 발생 시 503을 반환해야 한다."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API 호출 실패")

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)

    @patch("recommendations.services.openai.OpenAI")
    def test_recommendation_includes_isbn(self, mock_openai_class):
        """GPT 응답에 isbn 필드가 포함될 때 recommendations 각 항목에 isbn 키가 있어야 한다."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "recommendations": [
                    {
                        "title": "채식주의자",
                        "author": "한강",
                        "reason": "취향에 맞는 책입니다.",
                        "isbn": "9788936433598",
                    }
                ]
            }
        )
        mock_client.chat.completions.create.return_value = mock_response

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendations", response.data)
        for item in response.data["recommendations"]:
            self.assertIn("isbn", item)
