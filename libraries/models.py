from django.db import models


class Library(models.Model):
    name = models.CharField(max_length=200, verbose_name="도서관명")
    address = models.CharField(max_length=300, verbose_name="도로명 주소")
    latitude = models.FloatField(verbose_name="위도")
    longitude = models.FloatField(verbose_name="경도")
    phone = models.CharField(max_length=50, blank=True, verbose_name="전화번호")
    homepage = models.URLField(blank=True, verbose_name="홈페이지 URL")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최종 동기화 시각")

    class Meta:
        ordering = ["name"]
        verbose_name = "도서관"
        verbose_name_plural = "도서관 목록"

    def __str__(self):
        return self.name
