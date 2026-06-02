import os
from datetime import date

import requests

from .models import Library

SEOUL_API_BASE = "http://openapi.seoul.go.kr:8088"


def fetch_libraries_from_api() -> list[dict]:
    """서울 열린데이터 광장 SeoulPublicLibraryInfo API 호출 → 파싱된 dict 리스트 반환"""
    api_key = os.environ.get("SEOUL_API_KEY")
    if not api_key:
        raise ValueError("SEOUL_API_KEY 환경변수가 설정되지 않았습니다.")
    url = f"{SEOUL_API_BASE}/{api_key}/json/SeoulPublicLibraryInfo/1/1000/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    rows = data.get("SeoulPublicLibraryInfo", {}).get("row", [])
    result = []
    for row in rows:
        try:
            lat = float(row.get("YDNTS", 0) or 0)
            lng = float(row.get("XCNTS", 0) or 0)
        except (ValueError, TypeError):
            continue
        if lat == 0 or lng == 0:
            continue
        result.append(
            {
                "name": row.get("LBRRY_NAME", "").strip(),
                "address": row.get("ADRES", "").strip(),
                "latitude": lat,
                "longitude": lng,
                "phone": row.get("TEL_NO", "").strip(),
                "homepage": row.get("HMPG_URL", "").strip(),
            }
        )
    return result


def sync_libraries():
    """DB 캐시 확인 → 오늘 날짜 데이터 없으면 API 호출 후 upsert → QuerySet 반환"""
    today = date.today()
    if Library.objects.filter(updated_at__date=today).exists():
        return Library.objects.all()
    libraries_data = fetch_libraries_from_api()
    for lib in libraries_data:
        Library.objects.update_or_create(
            name=lib["name"],
            defaults={
                "address": lib["address"],
                "latitude": lib["latitude"],
                "longitude": lib["longitude"],
                "phone": lib["phone"],
                "homepage": lib["homepage"],
            },
        )
    return Library.objects.all()
