from django.urls import path

from .views import BookPriceView

urlpatterns = [
    path("prices/", BookPriceView.as_view(), name="book-prices"),
]
