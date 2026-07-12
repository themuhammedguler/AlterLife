"""
Library Router – /api/v1/library
Kullanıcının eğitim kütüphanesi: kaynak ekle, tamamla, sil
"""

import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_library, save_library, get_user, save_user

router = APIRouter(prefix="/library")


# ── Schemas ───────────────────────────────────────────────────────────────────

class LibraryResource(BaseModel):
    resource_id: str
    title: str
    platform: str
    url: str
    thumbnail_url: Optional[str] = None
    skill_tags: List[str] = []
    saved_at: str
    is_completed: bool = False
    completed_at: Optional[str] = None
    xp_reward: int = 50


class SaveResourceRequest(BaseModel):
    title: str
    platform: str
    url: str
    thumbnail_url: Optional[str] = None
    skill_tags: List[str] = []


class CompleteResourceResponse(BaseModel):
    resource_id: str
    is_completed: bool
    xp_earned: int
    new_total_xp: int
    message: str


# ── Default seeder (first visit) ─────────────────────────────────────────────

DEFAULT_RESOURCES = [
    {
        "resource_id": "res_seed_001",
        "title": "AWS VPC Tutorial for Beginners",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=2doSoMN2xvI",
        "thumbnail_url": None,
        "skill_tags": ["AWS", "Cloud", "VPC"],
        "saved_at": "2026-06-28",
        "is_completed": False,
        "completed_at": None,
        "xp_reward": 50,
    },
    {
        "resource_id": "res_seed_002",
        "title": "Docker & Kubernetes: The Complete Guide",
        "platform": "Udemy",
        "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
        "thumbnail_url": None,
        "skill_tags": ["Docker", "Kubernetes", "DevOps"],
        "saved_at": "2026-06-27",
        "is_completed": True,
        "completed_at": "2026-07-01",
        "xp_reward": 50,
    },
    {
        "resource_id": "res_seed_003",
        "title": "FastAPI – Official Documentation",
        "platform": "Docs",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "thumbnail_url": None,
        "skill_tags": ["Python", "FastAPI", "Backend"],
        "saved_at": "2026-06-26",
        "is_completed": False,
        "completed_at": None,
        "xp_reward": 50,
    },
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/resources", response_model=List[LibraryResource], summary="Kütüphanedeki kaynakları listele")
async def list_resources(user_id: str = Depends(get_current_user_id)):
    resources = get_library(user_id)
    if not resources:
        # Seed default resources on first visit
        save_library(user_id, DEFAULT_RESOURCES)
        return [LibraryResource(**r) for r in DEFAULT_RESOURCES]
    return [LibraryResource(**r) for r in resources]


@router.post("/resources", response_model=LibraryResource, summary="Kaynağı kütüphaneye kaydet")
async def save_resource(payload: SaveResourceRequest, user_id: str = Depends(get_current_user_id)):
    resources = get_library(user_id)
    if not resources:
        resources = list(DEFAULT_RESOURCES)

    new_resource = {
        "resource_id": f"res_{uuid.uuid4().hex[:8]}",
        "title": payload.title,
        "platform": payload.platform,
        "url": payload.url,
        "thumbnail_url": payload.thumbnail_url,
        "skill_tags": payload.skill_tags,
        "saved_at": str(date.today()),
        "is_completed": False,
        "completed_at": None,
        "xp_reward": 50,
    }
    resources.append(new_resource)
    save_library(user_id, resources)
    return LibraryResource(**new_resource)


@router.patch("/resources/{resource_id}/complete", response_model=CompleteResourceResponse, summary="Kaynağı tamamlandı işaretle")
async def complete_resource(resource_id: str, user_id: str = Depends(get_current_user_id)):
    resources = get_library(user_id)
    if not resources:
        resources = list(DEFAULT_RESOURCES)

    target = next((r for r in resources if r["resource_id"] == resource_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"'{resource_id}' kütüphanede bulunamadı.")
    if target["is_completed"]:
        raise HTTPException(status_code=400, detail="Bu kaynak zaten tamamlandı.")

    target["is_completed"] = True
    target["completed_at"] = str(date.today())
    save_library(user_id, resources)

    # Award XP to user profile
    user = get_user(user_id) or {}
    xp_reward = target.get("xp_reward", 50)
    current_xp = user.get("xp", 0) + xp_reward
    current_level = user.get("level", 1)
    next_level_xp = current_level * 1000
    if current_xp >= next_level_xp:
        current_level += 1
    user.update({"xp": current_xp, "level": current_level, "next_level_xp": current_level * 1000})
    save_user(user_id, user)

    return CompleteResourceResponse(
        resource_id=resource_id,
        is_completed=True,
        xp_earned=xp_reward,
        new_total_xp=current_xp,
        message=f"✅ Kaynak tamamlandı! +{xp_reward} XP kazandın.",
    )


@router.delete("/resources/{resource_id}", summary="Kaynağı sil")
async def delete_resource(resource_id: str, user_id: str = Depends(get_current_user_id)):
    resources = get_library(user_id)
    if not resources:
        resources = list(DEFAULT_RESOURCES)

    original_count = len(resources)
    resources = [r for r in resources if r["resource_id"] != resource_id]
    if len(resources) == original_count:
        raise HTTPException(status_code=404, detail=f"'{resource_id}' bulunamadı.")

    save_library(user_id, resources)
    return {"message": f"Kaynak '{resource_id}' silindi.", "deleted": True}
