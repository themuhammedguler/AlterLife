"""
User Router – /api/v1/user
Kullanıcı profili, onboarding ve avatar yönetimi
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/user")


# ── Request / Response Schemas ────────────────────────────────────────────────

class OnboardingRequest(BaseModel):
    role: str                   # Örn: "Junior Web Developer"
    skills: dict                # Örn: {"Python": "Intermediate"}
    languages: dict             # Örn: {"English": "B2", "German": "A1"}
    monthly_savings_usd: float
    total_savings_usd: float


class AvatarGenerateRequest(BaseModel):
    description: Optional[str] = None   # Text-to-Image: fiziksel betimleme
    photo_base64: Optional[str] = None  # Image-to-Image: fotoğraf


class UserProfileResponse(BaseModel):
    user_id: str
    display_name: str
    email: str
    role: str
    level: int
    xp: int
    next_level_xp: int
    title: str
    avatar_url: Optional[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/onboarding", summary="Kullanıcı onboarding – karakter sınıfı ve yetenekler")
async def onboarding(payload: OnboardingRequest):
    """
    Kayıt sonrası RPG karakter oluşturma verilerini Firestore'a kaydeder.
    TODO: Firebase Firestore write + Gemini ile ilk yol haritası üretimi
    """
    raise HTTPException(status_code=501, detail="Hafta 2'de implement edilecek.")


@router.post("/avatar/generate", summary="AI RPG avatar üretimi")
async def generate_avatar(payload: AvatarGenerateRequest):
    """
    Text veya fotoğraftan Gemini Vision + Imagen ile RPG avatar üretir.
    TODO: Gemini Vision + Imagen 3 entegrasyonu
    """
    raise HTTPException(status_code=501, detail="Hafta 2'de implement edilecek.")


@router.get("/profile", response_model=UserProfileResponse, summary="Kullanıcı profili")
async def get_profile():
    """
    Kullanıcının profil, XP ve seviye bilgilerini döner.
    TODO: Firebase Auth'dan user_id çıkar, Firestore'dan profil yükle
    """
    # Placeholder data for development
    return UserProfileResponse(
        user_id="dev_user_001",
        display_name="Test Kullanıcı",
        email="test@alterlife.io",
        role="Junior Web Developer",
        level=1,
        xp=0,
        next_level_xp=1000,
        title="Novice Seeker",
        avatar_url=None,
    )
