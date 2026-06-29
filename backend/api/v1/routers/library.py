"""
Library Router – /api/v1/library
AI'ın önerdiği ve kullanıcının kaydettiği eğitim kaynakları
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/library")


# ── Schemas ───────────────────────────────────────────────────────────────────

class LibraryResource(BaseModel):
    resource_id: str
    title: str
    platform: str               # "YouTube" | "Udemy" | "Article" | "Docs"
    url: str
    thumbnail_url: Optional[str]
    skill_tags: List[str]       # Örn: ["AWS", "Cloud", "Networking"]
    saved_at: str
    is_completed: bool = False


class SaveResourceRequest(BaseModel):
    title: str
    platform: str
    url: str
    thumbnail_url: Optional[str]
    skill_tags: List[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/resources", response_model=List[LibraryResource], summary="Kütüphanedeki kaynakları listele")
async def list_resources():
    """
    Kullanıcının kaydettiği ve AI'ın önerdiği tüm kaynakları döner.
    TODO: Firestore'dan yükle – Hafta 3
    """
    # Placeholder
    return [
        LibraryResource(
            resource_id="res_001",
            title="AWS VPC Tutorial for Beginners",
            platform="YouTube",
            url="https://www.youtube.com/watch?v=example",
            thumbnail_url="https://i.ytimg.com/vi/example/hqdefault.jpg",
            skill_tags=["AWS", "Cloud", "VPC"],
            saved_at="2026-06-28",
            is_completed=False,
        ),
    ]


@router.post("/resources", summary="Kaynağı kütüphaneye kaydet")
async def save_resource(payload: SaveResourceRequest):
    """
    Kullanıcının seçtiği kaynağı kütüphaneye ekler.
    TODO: Firestore write – Hafta 3
    """
    raise HTTPException(status_code=501, detail="Kaynak kaydetme Hafta 3'te eklenecek.")
