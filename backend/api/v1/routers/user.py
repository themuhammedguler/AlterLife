"""
User Router – /api/v1/user
Kullanıcı profili, onboarding ve avatar yönetimi
"""

import os
import hashlib
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from api.v1.auth_utils import get_current_user_id
from api.v1.database import delete_user_data, get_user, save_user
from api.v1.services.simulation_service import generate_initial_tree_data
from api.v1.services.avatar_service import generate_avatar as avatar_service_generate

router = APIRouter(prefix="/user")

# ── Request / Response Schemas ────────────────────────────────────────────────

class OnboardingRequest(BaseModel):
    # Standard schema
    role: Optional[str] = None                   # Örn: "Junior Web Developer"
    skills: Optional[dict] = None                # Örn: {"Python": "Intermediate"}
    languages: Optional[dict] = None             # Örn: {"English": "B2", "German": "A1"}
    monthly_savings_usd: Optional[float] = 0.0
    total_savings_usd: Optional[float] = 0.0

    # Frontend-compatible schema (fallback)
    status: Optional[str] = None
    age: Optional[str] = None
    city: Optional[str] = None
    field: Optional[str] = None
    workPrefs: Optional[List[str]] = None
    freeGoal: Optional[str] = None


class AvatarGenerateRequest(BaseModel):
    description: Optional[str] = None   # Text-to-Image: fiziksel betimleme
    photo_base64: Optional[str] = None  # Image-to-Image: fotoğraf
    photo_mime_type: str = Field(default="image/jpeg", pattern=r"^image/(jpeg|png|webp)$")


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
    energy: int = 100
    focus: int = 100
    max_energy: int = 100
    max_focus: int = 100
    daily_preferences: Dict[str, Any] = Field(default_factory=dict)


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    role: Optional[str] = Field(default=None, min_length=2, max_length=120)
    experience_years: Optional[int] = Field(default=None, ge=0, le=80)
    daily_preferences: Optional[Dict[str, Any]] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/onboarding", summary="Kullanıcı onboarding – karakter sınıfı ve yetenekler")
async def onboarding(payload: OnboardingRequest, user_id: str = Depends(get_current_user_id)):
    """
    Kayıt sonrası RPG karakter oluşturma verilerini Firestore'a veya yerel DB'ye kaydeder.
    Ardından kullanıcının hedefine yönelik ilk dallanan karar ağacını (simulation tree) oluşturur.
    """
    user_data = get_user(user_id)
    if not user_data:
        # Fallback profile if user was not registered via OAuth
        user_data = {
            "userId": user_id,
            "email": f"{user_id}@alterlife.io",
            "displayName": "AlterLife Gezgini",
            "createdAt": "2026-07-08T00:00:00Z"
        }

    # Normalize role/field/goal
    role = payload.role or payload.field or "Software Developer"
    if role == "software":
        role = "Software Developer"
    elif role == "design":
        role = "UI/UX Designer"
    elif role == "finance":
        role = "Financial Analyst"
    elif role == "startup":
        role = "Startup Founder"

    # Set up profile dict
    profile_data = {
        "role": role,
        "experienceYears": 1,
        "skills": payload.skills or {},
        "languages": payload.languages or {},
        "avatarUrl": user_data.get("profile", {}).get("avatarUrl"),
        "city": payload.city or "İstanbul, Türkiye",
        "age": payload.age or "24",
        "status": payload.status or "seeking",
        "workPrefs": payload.workPrefs or [],
        "freeGoal": payload.freeGoal or "2 yıl içinde yurt dışında çalışmak"
    }

    # Every user receives a persistent, directly displayable avatar during
    # onboarding. OpenAI Images is used when configured; otherwise the same
    # user-specific prompt deterministically produces a unique DiceBear image.
    if not profile_data["avatarUrl"]:
        identity_seed = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
        avatar_description = (
            f"Unique futuristic RPG explorer, role: {role}, "
            f"goal: {profile_data['freeGoal']}, identity seed: {identity_seed}. "
            "Create a visually distinctive face, outfit, color palette and accessories."
        )
        avatar_result = avatar_service_generate(
            user_id=user_id,
            description=avatar_description,
            role=role,
        )
        profile_data["avatarUrl"] = avatar_result.get("avatar_url")

    user_data["profile"] = profile_data
    
    # Initialize or reset RPG state
    user_data["rpgState"] = {
        "level": 1,
        "xp": 100, # Start with some XP
        "next_level_xp": 1000,
        "title": "Novice Seeker"
    }

    # Save user to DB
    save_user(user_id, user_data)

    # Automatically trigger initial simulation tree generation
    target = payload.freeGoal or f"Become a Senior {role}"
    try:
        # Generate simulation tree and save it
        simulation_id = f"sim_{user_id}"
        generate_initial_tree_data(simulation_id, user_id, target, profile_data)
    except Exception as e:
        print(f"[Onboarding] Error generating initial tree: {e}")

    return {
        "status": "success",
        "message": "Onboarding completed, initial decision tree generated.",
        "user_id": user_id,
        "simulation_id": f"sim_{user_id}",
        "avatar_url": profile_data.get("avatarUrl"),
    }


@router.post("/avatar/generate", summary="AI RPG avatar üretimi")
async def generate_avatar(payload: AvatarGenerateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Metin veya fotoğraftan Groq Vision + DiceBear ile fütüristik/RPG avatarı üretir.
    """
    user_data = get_user(user_id) or {}
    role = user_data.get("profile", {}).get("role", "Software Developer")

    result = avatar_service_generate(
        user_id=user_id,
        description=payload.description,
        photo_base64=payload.photo_base64.split(",")[-1] if payload.photo_base64 else None,
        photo_mime_type=payload.photo_mime_type,
        role=role
    )

    # Save avatar URL to user profile
    if result.get("avatar_url"):
        if "profile" not in user_data:
            user_data["profile"] = {}
        user_data["profile"]["avatarUrl"] = result["avatar_url"]
        save_user(user_id, user_data)

    return {
        "status": "success",
        "avatar_url": result["avatar_url"],
        "avatar_type": result.get("avatar_type", "dicebear"),
        "message": result.get("message", "Avatar oluşturuldu."),
        "description": result.get("prompt_used", "")
    }


@router.get("/profile", response_model=UserProfileResponse, summary="Kullanıcı profili")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının profil, XP, seviye ve Energy/Focus bilgilerini döner.
    """
    user_data = get_user(user_id)
    if not user_data:
        user_data = {
            "userId": user_id,
            "email": f"{user_id}@alterlife.io",
            "displayName": "Test Kullanıcı",
            "createdAt": "2026-07-08T00:00:00Z",
            "profile": {
                "role": "Junior Web Developer",
                "experienceYears": 1,
                "skills": {},
                "languages": {},
                "avatarUrl": None
            },
            "rpgState": {
                "level": 1,
                "xp": 0,
                "next_level_xp": 1000,
                "title": "Novice Seeker",
                "energy": 100,
                "focus": 100,
                "max_energy": 100,
                "max_focus": 100
            }
        }
        save_user(user_id, user_data)

    profile = user_data.get("profile", {})
    rpg_state = user_data.get("rpgState", {})

    return UserProfileResponse(
        user_id=user_id,
        display_name=user_data.get("displayName", "Test Kullanıcı"),
        email=user_data.get("email", "test@alterlife.io"),
        role=profile.get("role", "Gezgin"),
        level=rpg_state.get("level", 1),
        xp=rpg_state.get("xp", 0),
        next_level_xp=rpg_state.get("next_level_xp", 1000),
        title=rpg_state.get("title", "Novice Seeker"),
        avatar_url=profile.get("avatarUrl"),
        energy=rpg_state.get("energy", 100),
        focus=rpg_state.get("focus", 100),
        max_energy=rpg_state.get("max_energy", 100),
        max_focus=rpg_state.get("max_focus", 100),
        daily_preferences=user_data.get("dailyPreferences", {}),
    )


@router.patch("/profile", response_model=UserProfileResponse, summary="Kullanıcı profilini güncelle")
async def update_profile(payload: UserProfileUpdate, user_id: str = Depends(get_current_user_id)):
    user_data = get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")

    if payload.display_name is not None:
        user_data["displayName"] = payload.display_name.strip()
    profile = user_data.setdefault("profile", {})
    if payload.role is not None:
        profile["role"] = payload.role.strip()
    if payload.experience_years is not None:
        profile["experienceYears"] = payload.experience_years
    if payload.daily_preferences is not None:
        user_data["dailyPreferences"] = {
            "day_type": payload.daily_preferences.get("day_type", "normal"),
            "best_focus_time": payload.daily_preferences.get("best_focus_time", "evening"),
            "mood": payload.daily_preferences.get("mood", "playful"),
            "available_minutes": int(payload.daily_preferences.get("available_minutes", 60)),
            "include_social": bool(payload.daily_preferences.get("include_social", True)),
        }
    save_user(user_id, user_data)
    return await get_profile(user_id)


@router.delete("/account", summary="Hesabı ve kullanıcı verilerini kalıcı olarak sil")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    if not get_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    try:
        from api.v1.database import get_db_mode
        if get_db_mode() == "firestore":
            from firebase_admin import auth as firebase_auth
            firebase_auth.delete_user(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Kimlik hesabı silinemedi: {exc}",
        ) from exc
    delete_user_data(user_id)
    return {"status": "deleted"}


@router.post("/rest", summary="😴 Dinlenme – Energy & Focus yenile")
async def rest(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının Energy ve Focus değerlerini tam yeniler.
    Karşılığında 'Dinlendin' adında küçük bir XP bonusu verilir.
    """
    user_data = get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

    rpg_state = user_data.get("rpgState", {})
    rpg_state["energy"] = rpg_state.get("max_energy", 100)
    rpg_state["focus"] = rpg_state.get("max_focus", 100)
    # Small XP bonus for resting
    rpg_state["xp"] = rpg_state.get("xp", 0) + 25
    user_data["rpgState"] = rpg_state
    save_user(user_id, user_data)

    return {
        "status": "success",
        "message": "Dinlenmeni tamamladın! Energy ve Focus yenilendi. +25 XP kazandın.",
        "energy": rpg_state["energy"],
        "focus": rpg_state["focus"],
        "xp_gained": 25
    }
