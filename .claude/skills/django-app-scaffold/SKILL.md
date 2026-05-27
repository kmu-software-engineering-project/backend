---
name: django-app-scaffold
description: "도서 추천 플랫폼에 새 Django 앱을 생성하고 기본 구조를 초기화하는 스킬. 새 앱 생성, 기본 파일(models, serializers, views, urls, tests) 초기화, INSTALLED_APPS 등록 요청 시 반드시 사용. 'startapp', '새 앱 만들어줘', '{앱이름} 앱 추가', '앱 구조 생성' 요청 시 트리거. book-platform-orchestrator의 Phase 2와 함께 사용되기도 한다."
---

# Django App Scaffold

도서 추천 플랫폼에 새 Django 앱을 생성하고 기본 구조를 초기화한다.

## 앱 이름 규칙

| 앱 이름 | 담당 기능 |
|---------|---------|
| `books` | 도서 정보, 장르 탐색 |
| `recommendations` | 맞춤 도서 추천 |
| `reviews` | 평점 및 리뷰 |
| `bookstores` | 온라인 서점 최저가 비교 |
| `libraries` | 서울시 도서관 위치 |

## 실행 순서

### Step 1: 앱 생성

```bash
uv run python manage.py startapp {앱이름}
```

### Step 2: INSTALLED_APPS 등록

`config/settings.py`에 앱 추가:

```python
INSTALLED_APPS = [
    # ...기존 앱들...
    "{앱이름}",
]
```

### Step 3: models.py 기본 구조

모든 모델은 타임스탬프 필드를 포함한다:

```python
from django.db import models


class {ModelName}(models.Model):
    # 필드 정의

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "{한글 모델명}"
        verbose_name_plural = "{한글 모델명 복수}"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.{대표필드}}"
```

### Step 4: serializers.py 기본 구조

```python
from rest_framework import serializers

from .models import {ModelName}


class {ModelName}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {ModelName}
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
```

### Step 5: views.py 기본 구조

```python
from rest_framework import viewsets

from .models import {ModelName}
from .serializers import {ModelName}Serializer


class {ModelName}ViewSet(viewsets.ModelViewSet):
    queryset = {ModelName}.objects.all()
    serializer_class = {ModelName}Serializer
```

### Step 6: urls.py 기본 구조

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import {ModelName}ViewSet

router = DefaultRouter()
router.register(r"{url-prefix}", {ModelName}ViewSet, basename="{basename}")

urlpatterns = [
    path("", include(router.urls)),
]
```

### Step 7: config/urls.py에 등록

```python
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/{앱url}/", include("{앱이름}.urls")),
]
```

### Step 8: tests.py 기본 구조

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import {ModelName}


class {ModelName}APITestCase(APITestCase):
    def setUp(self):
        self.{instance} = {ModelName}.objects.create(
            # 필수 필드 값 설정
        )

    def test_list(self):
        url = reverse("{basename}-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail(self):
        url = reverse("{basename}-detail", kwargs={"pk": self.{instance}.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Step 9: 마이그레이션

```bash
uv run python manage.py makemigrations {앱이름}
uv run python manage.py migrate
```

## 완료 체크리스트

- [ ] `uv run python manage.py startapp {앱이름}` 실행 완료
- [ ] `config/settings.py` INSTALLED_APPS에 등록
- [ ] `{앱이름}/models.py` — 모델 정의 (created_at, updated_at 포함)
- [ ] `{앱이름}/serializers.py` — ModelSerializer 기본 구조
- [ ] `{앱이름}/views.py` — ViewSet 기본 구조
- [ ] `{앱이름}/urls.py` — Router 설정
- [ ] `{앱이름}/tests.py` — APITestCase 기본 구조
- [ ] `config/urls.py` — `/api/v1/` prefix로 앱 URL include 등록
- [ ] 마이그레이션 완료
