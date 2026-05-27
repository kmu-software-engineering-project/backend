---
name: drf-api-builder
description: "Django REST Framework API 구현 가이드 스킬. Serializer, ViewSet, 커스텀 액션, 외부 API 연동, 페이지네이션, 필터링, 검색 구현 시 반드시 사용. 'API 만들어줘', 'serializer 작성', 'viewset 구현', '외부 API 연동', 'DRF 설정', '검색/필터 기능' 요청 시 트리거. django-app-scaffold 이후 API 상세 구현 단계에서 사용."
---

# DRF API Builder

Django REST Framework를 사용하여 도서 추천 플랫폼 API를 구현하는 가이드.

## Serializer 패턴

### 기본 ModelSerializer

```python
from rest_framework import serializers

from .models import {Model}


class {Model}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {Model}
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
```

### 중첩 관계 (읽기 전용)

```python
class {Model}DetailSerializer(serializers.ModelSerializer):
    related = {Related}Serializer(read_only=True)

    class Meta:
        model = {Model}
        fields = "__all__"
```

### 쓰기 전용 필드

```python
class {Model}Serializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = {Model}
        fields = "__all__"
```

## ViewSet 패턴

### 기본 ModelViewSet

```python
from rest_framework import viewsets

from .models import {Model}
from .serializers import {Model}Serializer


class {Model}ViewSet(viewsets.ModelViewSet):
    queryset = {Model}.objects.all()
    serializer_class = {Model}Serializer
```

### 커스텀 액션

```python
from rest_framework.decorators import action
from rest_framework.response import Response


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=["get"], url_path="featured")
    def featured(self, request):
        queryset = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="similar")
    def similar(self, request, pk=None):
        book = self.get_object()
        similar = Book.objects.filter(genre=book.genre).exclude(pk=book.pk)[:5]
        serializer = self.get_serializer(similar, many=True)
        return Response(serializer.data)
```

## URL Router 등록

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import {Model}ViewSet

router = DefaultRouter()
router.register(r"{url-prefix}", {Model}ViewSet, basename="{basename}")

urlpatterns = [
    path("", include(router.urls)),
]
```

## 외부 API 연동

외부 API 키는 `.env`에서만 로드한다. 타임아웃과 에러 처리를 반드시 포함한다:

```python
import os

import requests
from rest_framework import status
from rest_framework.response import Response


def fetch_bookstore_prices(isbn):
    api_key = os.getenv("BOOKSTORE_API_KEY")
    try:
        response = requests.get(
            "https://api.bookstore.example.com/prices",
            params={"isbn": isbn, "key": api_key},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


# View에서 사용
class BookstoreViewSet(viewsets.ViewSet):
    def list(self, request):
        isbn = request.query_params.get("isbn")
        data = fetch_bookstore_prices(isbn)
        if data is None:
            return Response(
                {"error": "외부 서점 API 연결 실패"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(data)
```

## 검색 및 필터링

```python
# config/settings.py에 추가
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# views.py
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    search_fields = ["title", "author"]      # ?search=파이썬
    ordering_fields = ["created_at", "title"] # ?ordering=-created_at
```

## 페이지네이션

```python
# config/settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

## API 엔드포인트 규칙

| 작업 | HTTP | URL 패턴 |
|------|------|---------|
| 목록 조회 | GET | `/api/v1/{resource}/` |
| 생성 | POST | `/api/v1/{resource}/` |
| 상세 조회 | GET | `/api/v1/{resource}/{id}/` |
| 수정 | PUT/PATCH | `/api/v1/{resource}/{id}/` |
| 삭제 | DELETE | `/api/v1/{resource}/{id}/` |
| 커스텀 액션 (컬렉션) | GET/POST | `/api/v1/{resource}/{action}/` |
| 커스텀 액션 (인스턴스) | GET/POST | `/api/v1/{resource}/{id}/{action}/` |

URL은 반드시 `kebab-case`를 사용한다: `/api/v1/book-recommendations/`

## 주의사항

- 외부 API 키는 절대 코드에 하드코딩하지 않는다
- `AllowAny` 권한은 개발 환경 한정이다
- 마이그레이션 없이 모델을 사용하면 `OperationalError`가 발생한다 — `migrate`를 먼저 실행한다
- `config/urls.py`에 앱 URL을 `include`하지 않으면 API가 404를 반환한다
