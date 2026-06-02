from django.urls import path

from .views import LibraryDetailView, LibraryListView, LibraryMapConfigView

urlpatterns = [
    path("", LibraryListView.as_view(), name="library-list"),
    path("map-config/", LibraryMapConfigView.as_view(), name="library-map-config"),
    path("<int:pk>/", LibraryDetailView.as_view(), name="library-detail"),
]
