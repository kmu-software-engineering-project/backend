import os
import re
from urllib.parse import quote

import requests

NAVER_BOOK_API_URL = "https://openapi.naver.com/v1/search/book.json"

# 한국 출판사 ISBN 접두사 (9788: 기존, 9791: 신규)
KOREAN_ISBN_PREFIXES = ("9788", "9791")

KNOWN_BOOKSTORES = [
    {
        "store_name": "알라딘",
        "url_template": (
            "https://www.aladin.co.kr/search/wsearchresult.aspx"
            "?SearchTarget=Book&SearchWord={query}"
        ),
    },
    {
        "store_name": "교보문고",
        "url_template": "https://search.kyobobook.co.kr/search?keyword={query}",
    },
    {
        "store_name": "YES24",
        "url_template": "https://www.yes24.com/Product/Search?query={query}",
    },
    {
        "store_name": "인터파크",
        "url_template": (
            "https://book.interpark.com/search/bookSearch.do?query={query}"
        ),
    },
]


def _build_store_links(query: str) -> list:
    """각 서점의 검색 URL을 생성한다."""
    encoded = quote(query)
    return [
        {
            "store_name": store["store_name"],
            "price": None,
            "purchase_url": store["url_template"].format(query=encoded),
        }
        for store in KNOWN_BOOKSTORES
    ]


def _search_naver_books(query: str, headers: dict, author: str = "") -> list:
    """네이버 도서 검색 API를 호출하여 items 리스트를 반환한다.
    author를 전달하면 d_auth 파라미터로 분리하여 검색 정확도를 높인다.
    """
    params = {"query": query, "display": 10}
    if author:
        params["d_auth"] = author
    response = requests.get(
        NAVER_BOOK_API_URL,
        headers=headers,
        params=params,
        timeout=5,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def _titles_match(searched: str, found: str) -> bool:
    """검색 제목이 네이버 반환 제목과 일치하는지 느슨하게 확인한다.
    네이버 API는 제목에 <b> 태그를 포함할 수 있으므로 제거 후 비교한다.
    """
    clean_found = re.sub(r"<[^>]+>", "", found).strip()
    a, b = searched.strip(), clean_found
    return a in b or b in a


def _pick_korean_item(items: list, fallback: bool = False) -> dict | None:
    """
    검색 결과에서 한국어판(ISBN 9788/9791)을 우선 반환한다.
    fallback=True이면 한국어판이 없을 때 첫 번째 결과를 반환한다.
    fallback=False이면 한국어판이 없을 때 None을 반환한다.
    """
    for item in items:
        isbn = item.get("isbn", "")
        if any(isbn.startswith(prefix) for prefix in KOREAN_ISBN_PREFIXES):
            return item
    return (items[0] if items else None) if fallback else None


PRICE_STATUS_AVAILABLE = "available"
PRICE_STATUS_UNAVAILABLE = "unavailable"
PRICE_STATUS_UNKNOWN = "unknown"


def _parse_price(discount_str) -> tuple[int | None, str]:
    """
    discount 문자열을 파싱하여 (가격, 상태) 튜플을 반환한다.
    - (가격, "available")  : 판매 중
    - (None, "unavailable"): 품절/절판 (discount == "0")
    - (None, "unknown")    : 가격 정보 없음
    """
    try:
        price = int(discount_str)
        if price > 0:
            return price, PRICE_STATUS_AVAILABLE
        else:
            return None, PRICE_STATUS_UNAVAILABLE
    except (ValueError, TypeError):
        return None, PRICE_STATUS_UNKNOWN


def get_book_price_info(title: str, author: str = "", isbn: str = "") -> dict:
    """
    네이버 도서 검색 API로 책 정보 및 네이버 최저가 조회.
    - ISBN 검색 실패 시 제목+저자로 fallback 검색
    - 한국어판 ISBN(9788/9791) 우선 선택
    반환: {
        "book": {
            "title": str,
            "author": str,
            "isbn": str | None,
            "cover_url": str | None,
            "naver_lowest_price": int | None,
            "naver_price_status": "available" | "unavailable" | "unknown",
            "naver_price_compare_url": str | None,
        },
        "stores": [{"store_name": str, "price": None, "purchase_url": str}, ...]
    }
    """
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다."
        )

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    # 1차: ISBN 검색 → 한국어판만 선택, 제목 불일치 시 무시 (GPT ISBN hallucination 방어)
    # 2차: 한국어판 없거나 제목 불일치면 제목+저자로 fallback → 한국어판 우선, 없으면 첫 번째
    korean_item = None
    if isbn:
        items = _search_naver_books(isbn, headers)
        candidate = _pick_korean_item(items, fallback=False)
        if candidate and _titles_match(title, candidate.get("title", "")):
            korean_item = candidate

    if not korean_item:
        items = _search_naver_books(title, headers, author=author)
        korean_item = _pick_korean_item(items, fallback=True)

    if not korean_item:
        return {
            "book": {
                "title": title,
                "author": author,
                "isbn": isbn or None,
                "cover_url": None,
                "naver_lowest_price": None,
                "naver_price_status": PRICE_STATUS_UNKNOWN,
                "naver_price_compare_url": None,
            },
            "stores": _build_store_links(isbn if isbn else title),
        }

    found_isbn = korean_item.get("isbn", "").strip() or isbn or None
    cover_url = korean_item.get("image") or None
    naver_price_compare_url = korean_item.get("link") or None
    naver_lowest_price, naver_price_status = _parse_price(
        korean_item.get("discount", "")
    )

    store_query = found_isbn if found_isbn else title

    return {
        "book": {
            "title": title,
            "author": author,
            "isbn": found_isbn,
            "cover_url": cover_url,
            "naver_lowest_price": naver_lowest_price,
            "naver_price_status": naver_price_status,
            "naver_price_compare_url": naver_price_compare_url,
        },
        "stores": _build_store_links(store_query),
    }
