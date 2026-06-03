from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "book_title", "nickname", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["book_title", "nickname", "comment"]
    readonly_fields = ["password", "created_at"]
