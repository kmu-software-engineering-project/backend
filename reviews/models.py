from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    book_id = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="도서 ID",
    )
    book_title = models.CharField(max_length=500, verbose_name="도서 제목")
    nickname = models.CharField(max_length=50, verbose_name="닉네임")
    password = models.CharField(max_length=128, verbose_name="비밀번호")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="별점",
    )
    comment = models.CharField(max_length=100, verbose_name="한 줄 평")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성 시각")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰 목록"

    def __str__(self):
        return f"[{self.rating}★] {self.nickname} - {self.book_title[:30]}"
