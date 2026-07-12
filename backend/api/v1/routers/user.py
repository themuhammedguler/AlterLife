"""
User Router – /api/v1/user
Kullanıcı profili, onboarding ve avatar yönetimi
"""

import os
import hashlib
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, save_user
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
        "simulation_id": f"sim_{user_id}"
    }


@router.post("/avatar/generate", summary="AI RPG avatar üretimi")
async def generate_avatar(payload: AvatarGenerateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Metin veya fotoğraftan Gemini Vision + DiceBear ile fütüristik/RPG avatarı üretir.
    """
    user_data = get_user(user_id) or {}
    role = user_data.get("profile", {}).get("role", "Software Developer")

    result = avatar_service_generate(
        user_id=user_id,
        description=payload.description,
        photo_base64=payload.photo_base64.split(",")[-1] if payload.photo_base64 else None,
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
    )


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
