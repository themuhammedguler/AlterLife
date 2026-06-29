"""
Quests Router – /api/v1/quests
Günlük Görevler ve XP Doğrulama (GitHub + Calendar)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/quests")


# ── Schemas ───────────────────────────────────────────────────────────────────

class DailyQuest(BaseModel):
    quest_id: str
    title: str
    description: str
    xp_reward: int
    status: str             # "pending" | "completed" | "failed"
    verified_by: str        # "manual" | "calendar_sync" | "github_commit"
    resource_link: Optional[str]
    completed_at: Optional[str]


class QuestVerifyResponse(BaseModel):
    quest_id: str
    status: str
    xp_earned: int
    new_total_xp: int
    level_up: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/daily", response_model=List[DailyQuest], summary="Günlük görevleri getir")
async def get_daily_quests():
    """
    Kullanıcının aktif karar dalına göre bugünün 3 mikro görevini döner.
    TODO: Gemini QuestAgent + aktif milestone analizi – Hafta 2
    """
    # Placeholder – geliştirme için örnek görevler
    today = str(date.today())
    return [
        DailyQuest(
            quest_id="qst_001",
            title="AWS VPC Konusunu Çalış",
            description="AWS resmi dokümantasyonundan VPC bölümünü oku (20 dk).",
            xp_reward=150,
            status="pending",
            verified_by="calendar_sync",
            resource_link="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
            completed_at=None,
        ),
        DailyQuest(
            quest_id="qst_002",
            title="Docker Compose ile uygulama ayağa kaldır",
            description="Bu projenin docker-compose.yml dosyasını çalıştır ve servisleri kontrol et.",
            xp_reward=200,
            status="pending",
            verified_by="github_commit",
            resource_link=None,
            completed_at=None,
        ),
        DailyQuest(
            quest_id="qst_003",
            title="Almanca Duolingo – 10 dakika",
            description="Almanca kelime pratiği yap (A1-A2 seviyesi).",
            xp_reward=50,
            status="pending",
            verified_by="manual",
            resource_link="https://www.duolingo.com",
            completed_at=None,
        ),
    ]


@router.post("/{quest_id}/verify", response_model=QuestVerifyResponse, summary="Görevi tamamlandı olarak işaretle")
async def verify_quest(quest_id: str):
    """
    Görevi doğrular:
    - calendar_sync: Google Calendar'dan [AlterLife] etiketli etkinlik kontrol
    - github_commit: GitHub API'den bugünkü commit kontrol
    - manual: Kullanıcı onayı
    TODO: Google Calendar API + GitHub API entegrasyonu – Hafta 3
    """
    raise HTTPException(
        status_code=501,
        detail="Görev doğrulama (Calendar/GitHub) Hafta 3'te eklenecek. Şimdilik manuel onaylayın.",
    )
