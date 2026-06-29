"""
Auth Router – /api/v1/auth
Google OAuth JWT doğrulaması
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth")


class GoogleAuthRequest(BaseModel):
    id_token: str  # Google OAuth ID token from frontend


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_new_user: bool


@router.post("/google", response_model=AuthResponse, summary="Google OAuth ile giriş")
async def google_auth(payload: GoogleAuthRequest):
    """
    Frontend'den gelen Google ID token'ı doğrular,
    Firebase Auth ile eşleştirir ve JWT döner.
    TODO: Firebase token verification + JWT generation
    """
    # Placeholder – Hafta 2'de Firebase Admin SDK ile doldurulacak
    raise HTTPException(
        status_code=501,
        detail="Google OAuth doğrulaması henüz implement edilmedi. Hafta 2'de eklenecek.",
    )
