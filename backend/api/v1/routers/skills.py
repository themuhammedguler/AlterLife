"""
Skills Router – /api/v1/skills
Yetenek Ağacı ve YouTube/Udemy Kaynak Önerileri
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/skills")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SkillNode(BaseModel):
    skill_id: str
    name: str
    category: str           # Örn: "Cloud", "Language", "Soft Skill"
    level: int              # Kullanıcının mevcut seviyesi (0-5)
    xp: int
    is_unlocked: bool
    prerequisites: List[str] = []


class SkillResource(BaseModel):
    title: str
    platform: str           # "YouTube" | "Udemy" | "Official Docs"
    url: str
    thumbnail_url: Optional[str]
    rating: Optional[float]
    price: Optional[str]    # Udemy için


class SkillTreeResponse(BaseModel):
    nodes: List[SkillNode]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/tree", response_model=SkillTreeResponse, summary="İnteraktif yetenek ağacı")
async def get_skill_tree():
    """
    Kullanıcının kişiselleştirilmiş yetenek ağacını döner.
    TODO: Firestore'dan yükle, Gemini ile kişiselleştir – Hafta 3
    """
    # Placeholder veri
    return SkillTreeResponse(
        nodes=[
            SkillNode(
                skill_id="aws_fundamentals",
                name="AWS Fundamentals",
                category="Cloud",
                level=1,
                xp=200,
                is_unlocked=True,
                prerequisites=[],
            ),
            SkillNode(
                skill_id="aws_vpc",
                name="AWS VPC & Networking",
                category="Cloud",
                level=0,
                xp=0,
                is_unlocked=False,
                prerequisites=["aws_fundamentals"],
            ),
            SkillNode(
                skill_id="german_a1",
                name="Almanca A1",
                category="Language",
                level=2,
                xp=350,
                is_unlocked=True,
                prerequisites=[],
            ),
        ]
    )


@router.get("/{skill_name}/resources", response_model=List[SkillResource], summary="Yetenek kaynakları (YouTube/Udemy)")
async def get_skill_resources(skill_name: str):
    """
    Belirtilen yetenek için YouTube ve Udemy'den en iyi 3 kaynağı getirir.
    TODO: YouTube Data API v3 + Udemy API – Hafta 3
    """
    raise HTTPException(
        status_code=501,
        detail=f"'{skill_name}' için YouTube/Udemy kaynakları Hafta 3'te eklenecek.",
    )
