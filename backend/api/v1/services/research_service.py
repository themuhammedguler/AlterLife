"""
Live research helper.

Uses SerpAPI or Google Custom Search when configured, otherwise returns
high-trust fallback resources so the product keeps working without network keys.
"""

import os
from typing import List, Dict

import httpx


FALLBACK_RESULTS = [
    {
        "title": "Make it in Germany",
        "url": "https://www.make-it-in-germany.com/en/",
        "snippet": "Official guidance for working, visas, and living in Germany.",
        "source": "fallback",
    },
    {
        "title": "DAAD - Study in Germany",
        "url": "https://www.daad.de/en/studying-in-germany/",
        "snippet": "Official study programme and scholarship information.",
        "source": "fallback",
    },
    {
        "title": "Europass CV",
        "url": "https://europass.europa.eu/en/create-europass-cv",
        "snippet": "European CV builder for job and academic applications.",
        "source": "fallback",
    },
]


def search_live_resources(query: str, limit: int = 5) -> List[Dict[str, str]]:
    clean_query = query.strip()
    if not clean_query:
        return []

    serpapi_key = os.getenv("SERPAPI_API_KEY")
    google_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    google_cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")

    try:
        if serpapi_key:
            return _search_serpapi(clean_query, serpapi_key, limit)
        if google_key and google_cx:
            return _search_google_custom(clean_query, google_key, google_cx, limit)
    except Exception as exc:
        print(f"[Research] Live search failed: {exc}")

    return FALLBACK_RESULTS[:limit]


def _search_serpapi(query: str, api_key: str, limit: int) -> List[Dict[str, str]]:
    with httpx.Client(timeout=8.0) as client:
        response = client.get(
            "https://serpapi.com/search.json",
            params={"engine": "google", "q": query, "api_key": api_key, "num": limit},
        )
    response.raise_for_status()
    data = response.json()
    return [
        {
            "title": item.get("title", "Untitled"),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": "serpapi",
        }
        for item in data.get("organic_results", [])[:limit]
        if item.get("link")
    ]


def _search_google_custom(query: str, api_key: str, cx: str, limit: int) -> List[Dict[str, str]]:
    with httpx.Client(timeout=8.0) as client:
        response = client.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": cx, "q": query, "num": min(limit, 10)},
        )
    response.raise_for_status()
    data = response.json()
    return [
        {
            "title": item.get("title", "Untitled"),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": "google_custom_search",
        }
        for item in data.get("items", [])[:limit]
        if item.get("link")
    ]
