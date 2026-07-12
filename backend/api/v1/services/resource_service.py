import os
import httpx
from typing import List, Dict, Any

async def fetch_youtube_resources(query: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return []
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": query,
                    "maxResults": 3,
                    "type": "video",
                    "key": api_key
                }
            )
            if res.status_code == 200:
                items = res.json().get("items", [])
                results = []
                for item in items:
                    video_id = item.get("id", {}).get("videoId")
                    snippet = item.get("snippet", {})
                    results.append({
                        "title": snippet.get("title", "YouTube Video"),
                        "platform": "YouTube",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                        "level": "Beginner/Intermediate"
                    })
                return results
    except Exception:
        pass
    return []

async def fetch_udemy_resources(query: str) -> List[Dict[str, Any]]:
    client_id = os.getenv("UDEMY_CLIENT_ID")
    client_secret = os.getenv("UDEMY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []
    try:
        # Basic auth encoding
        auth = (client_id, client_secret)
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://www.udemy.com/api-2.0/courses/",
                auth=auth,
                params={
                    "search": query,
                    "page_size": 2,
                    "fields[course]": "title,url,price,image_240x135"
                }
            )
            if res.status_code == 200:
                courses = res.json().get("results", [])
                results = []
                for c in courses:
                    results.append({
                        "title": c.get("title", "Udemy Course"),
                        "platform": "Udemy",
                        "url": f"https://www.udemy.com{c.get('url')}",
                        "thumbnail_url": c.get("image_240x135"),
                        "level": "Paid"
                    })
                return results
    except Exception:
        pass
    return []

async def get_dynamic_resources(skill_name: str) -> List[Dict[str, Any]]:
    """
    Tries to search YouTube and Udemy, falls back to custom search query links if no API keys.
    """
    resources = []
    
    # 1. Try YouTube
    yt = await fetch_youtube_resources(skill_name)
    resources.extend(yt)
    
    # 2. Try Udemy
    ud = await fetch_udemy_resources(skill_name)
    resources.extend(ud)
    
    # 3. Fallback to constructed URLs if empty
    if not resources:
        resources.append({
            "title": f"YouTube: {skill_name} Eğitim Videoları",
            "platform": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={skill_name.replace(' ', '+')}",
            "level": "Genel"
        })
        resources.append({
            "title": f"Udemy: {skill_name} Kursları",
            "platform": "Udemy",
            "url": f"https://www.udemy.com/courses/search/?q={skill_name.replace(' ', '+')}",
            "level": "Ücretli/Ücretsiz"
        })
        resources.append({
            "title": f"Google Search: {skill_name} Rehberi",
            "platform": "Docs",
            "url": f"https://www.google.com/search?q={skill_name.replace(' ', '+')}+tutorial+documentation",
            "level": "Başlangıç"
        })
        
    return resources[:5]
