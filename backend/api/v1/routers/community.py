"""
Community Router – /api/v1/community
Topluluk başarı yolları, anonim paylaşım ve RAG tabanlı arama
"""

import base64
import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.services.rag_service import (
    build_community_overview,
    get_cohort_for_path,
    get_all_paths,
    get_user_memberships,
    join_path,
    search_similar_paths,
    anonymize_path,
    add_community_path
)

router = APIRouter(prefix="/community")


class PathSearchRequest(BaseModel):
    goal: str = Field(max_length=500)
    top_k: int = Field(default=4, ge=1, le=20)


class SharePathRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=500)
    steps: List[str] = Field(min_length=1, max_length=30)
    outcome: str = Field(min_length=2, max_length=1000)
    tags: List[str] = Field(default_factory=list, max_length=20)


class JoinPathRequest(BaseModel):
    branch: Optional[str] = Field(default=None, min_length=2, max_length=120)


@router.get("/paths", summary="🌍 Tüm topluluk başarı yollarını listele")
async def list_paths(limit: int = 20):
    """
    Topluluktan gelen anonim başarı yollarını döner.
    Filtreleme için limit parametresi kullanılabilir.
    """
    limit = min(max(limit, 1), 100)
    paths = get_all_paths(limit)
    return {"paths": [anonymize_path(p) for p in paths], "total": len(paths)}


@router.get("/overview", summary="🧭 Topluluk rota ve kohort özeti")
async def community_overview():
    """
    Topluluktaki rotaları ilerleme, aktif üye ve takılma sinyalleriyle özetler.
    """
    return build_community_overview(20)


@router.get("/paths/{path_id}/cohort", summary="👥 Bir rotanın kohort ilerlemesini getir")
async def path_cohort(path_id: str):
    """
    Seçili yolun anonim üye ilerlemelerini, ortak aşamasını ve ayrışan dallarını döner.
    """
    try:
        return get_cohort_for_path(path_id)
    except ValueError:
        return {"path_id": path_id, "members": [], "branches": [], "members_count": 0, "avg_progress": 0}


@router.post("/paths/{path_id}/join", summary="🤝 Bir topluluk rotasına anonim katıl")
async def join_community_path(
    path_id: str,
    payload: JoinPathRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Kullanıcıyı anonim şekilde seçili rotanın kohortuna dahil eder.
    """
    try:
        membership = join_path(user_id=user_id, path_id=path_id, branch=payload.branch)
    except ValueError:
        return {"status": "not_found", "message": "Rota bulunamadı."}
    return {"status": "joined", "membership": membership}


@router.post("/paths/{path_id}/invite", summary="🔗 Rota için arkadaş davet kodu oluştur")
async def create_path_invite(
    path_id: str,
    payload: JoinPathRequest,
    user_id: str = Depends(get_current_user_id),
):
    branch = payload.branch or "Ana rota"
    raw = json.dumps({"path_id": path_id, "branch": branch}, ensure_ascii=False).encode("utf-8")
    code = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
    return {
        "code": code,
        "path_id": path_id,
        "branch": branch,
        "share_text": f"AlterLife rotama katıl: {code}",
    }


@router.get("/invites/{code}", summary="🎟️ Davet kodunu çöz")
async def resolve_path_invite(code: str):
    try:
        padded = code + "=" * (-len(code) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))
        cohort = get_cohort_for_path(decoded["path_id"])
    except Exception:
        return {"status": "invalid", "message": "Davet kodu geçersiz."}
    return {
        "status": "valid",
        "path_id": decoded["path_id"],
        "branch": decoded.get("branch", "Ana rota"),
        "cohort": cohort,
    }


@router.get("/me/paths", summary="🧑‍🚀 Katıldığım topluluk rotaları")
async def my_community_paths(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının katıldığı anonim topluluk rotalarını döner.
    """
    return {"memberships": get_user_memberships(user_id)}


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
