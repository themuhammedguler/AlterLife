"""
Community Router – /api/v1/community
Topluluk başarı yolları, anonim paylaşım ve RAG tabanlı arama
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.services.rag_service import (
    get_all_paths,
    search_similar_paths,
    anonymize_path,
    add_community_path
)

router = APIRouter(prefix="/community")


class PathSearchRequest(BaseModel):
    goal: str
    top_k: int = 4


class SharePathRequest(BaseModel):
    goal: str
    steps: List[str]
    outcome: str
    tags: List[str] = []


@router.get("/paths", summary="🌍 Tüm topluluk başarı yollarını listele")
async def list_paths(limit: int = 20):
    """
    Topluluktan gelen anonim başarı yollarını döner.
    Filtreleme için limit parametresi kullanılabilir.
    """
    paths = get_all_paths(limit)
    return {"paths": [anonymize_path(p) for p in paths], "total": len(paths)}


@router.post("/paths/search", summary="🔍 Hedefe göre benzer yolları RAG ile bul")
async def search_paths(
    payload: PathSearchRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının girdiği hedefe göre toplulukta benzer başarı yollarını bulur.
    Cosine similarity tabanlı in-memory RAG arama kullanır.
    """
    if not payload.goal.strip():
        return {"paths": [], "query": ""}

    results = search_similar_paths(payload.goal, payload.top_k)
    return {
        "query": payload.goal,
        "paths": [anonymize_path(p) for p in results],
        "total": len(results)
    }


@router.post("/share", summary="📤 Kendi başarı yolunu anonim paylaş")
async def share_path(
    payload: SharePathRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının kendi başarı yolunu toplulukla anonim olarak paylaşır.
    """
    new_path = add_community_path(
        user_id=user_id,
        goal=payload.goal,
        steps=payload.steps,
        outcome=payload.outcome,
        tags=payload.tags
    )
    return {
        "status": "success",
        "message": "Başarı yolunuz anonim olarak paylaşıldı. Topluluğa katkın için teşekkürler!",
        "path_id": new_path["id"]
    }


@router.get("/stats", summary="📊 Topluluk istatistikleri")
async def community_stats():
    """
    Topluluk genelindeki istatistikleri döner.
    """
    paths = get_all_paths(100)
    countries_to = [p.get("country_to") for p in paths if p.get("country_to")]
    avg_duration = sum(p.get("duration_months", 12) for p in paths) / max(len(paths), 1)
    
    country_counts: dict = {}
    for c in countries_to:
        country_counts[c] = country_counts.get(c, 0) + 1

    top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_paths": len(paths),
        "success_rate": round(sum(1 for p in paths if p.get("success")) / max(len(paths), 1) * 100),
        "avg_duration_months": round(avg_duration, 1),
        "top_destinations": [{"country": c, "count": n} for c, n in top_countries],
        "active_members": len(paths) * 3  # Estimate
    }
