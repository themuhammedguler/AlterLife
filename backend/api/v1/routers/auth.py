"""
Auth Router – /api/v1/auth
Google OAuth JWT doğrulaması ve E-posta Girişi
"""

import hashlib
import os
import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from api.v1.auth_utils import create_access_token, hash_password, verify_password
from api.v1.database import get_user, save_user, get_db_mode

router = APIRouter(prefix="/auth")

class GoogleAuthRequest(BaseModel):
    id_token: str  # Google OAuth ID token from frontend

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=80)

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
    Eğer Firebase aktif değilse, mock doğrulama yapar.
    """
    id_token = payload.id_token
    user_id = None
    email = None
    display_name = "AlterLife Gezgini"
    is_new_user = False

    # 1. Firebase Admin SDK ile token doğrulama dene
    db_mode = get_db_mode()
    if db_mode == "firestore":
        try:
            from firebase_admin import auth as firebase_auth
            decoded_token = firebase_auth.verify_id_token(id_token)
            user_id = decoded_token["uid"]
            email = decoded_token.get("email")
            display_name = decoded_token.get("name", "AlterLife User")
        except Exception:
            # Token doğrulama hatası, fakat mock_token ise geliştirme ortamında kabul et
            if id_token.startswith("mock_token_"):
                email = id_token.replace("mock_token_", "") + "@alterlife.io"
                user_id = "usr_" + id_token.replace("mock_token_", "")
                display_name = id_token.replace("mock_token_", "").capitalize()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google ID token doğrulaması başarısız.",
                )
    else:
        # 2. Local Fallback / Mock Modu
        if id_token.startswith("mock_token_"):
            if os.getenv("ENVIRONMENT", "development").lower() == "production":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mock Google girişi production ortamında devre dışıdır.",
                )
            clean_token = id_token.replace("mock_token_", "")
            email = f"{clean_token}@alterlife.io"
            user_id = f"usr_{clean_token}"
            display_name = clean_token.capitalize()
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google girişi için Firebase yapılandırması gerekiyor.",
            )

    # 3. Kullanıcı kaydını kontrol et
    user_profile = get_user(user_id)
    if not user_profile:
        is_new_user = True
        # Temel profili oluştur
        new_user = {
            "userId": user_id,
            "email": email,
            "displayName": display_name,
            "createdAt": datetime_to_iso(),
            "profile": {
                "role": "Belirlenmedi",
                "experienceYears": 0,
                "skills": {},
                "languages": {},
                "avatarUrl": None
            },
            "rpgState": {
                "level": 1,
                "xp": 0,
                "next_level_xp": 1000,
                "title": "Novice Seeker"
            }
        }
        save_user(user_id, new_user)

    # 4. JWT access token üret
    access_token = create_access_token(data={"sub": user_id, "email": email})

    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        is_new_user=is_new_user
    )

@router.post("/email/register", response_model=AuthResponse, summary="E-posta ile kayıt ol")
async def email_register(payload: EmailRegisterRequest):
    """
    E-posta ve şifre ile yeni kullanıcı kaydeder (Mock/Local veya Firebase Auth).
    """
    email = payload.email
    password = payload.password
    display_name = payload.display_name
    
    # E-posta tabanlı kararlı bir local user ID üret
    user_id = "usr_" + hashlib.md5(email.lower().encode()).hexdigest()[:12]

    db_mode = get_db_mode()
    if db_mode == "firestore":
        try:
            from firebase_admin import auth as firebase_auth
            # Firebase Auth'a kaydet
            user_record = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            user_id = user_record.uid
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firebase Auth kaydı oluşturulamadı."
            )

    existing_user = get_user(user_id)
    if existing_user and existing_user.get("passwordHash"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kayıtlı.",
        )

    # Kullanıcı profilini kaydet
    new_user = {
        "userId": user_id,
        "email": email,
        "displayName": display_name,
        "createdAt": datetime_to_iso(),
        "profile": {
            "role": "Belirlenmedi",
            "experienceYears": 0,
            "skills": {},
            "languages": {},
            "avatarUrl": None
        },
        "rpgState": {
            "level": 1,
            "xp": 0,
            "next_level_xp": 1000,
            "title": "Novice Seeker"
        },
        **({"passwordHash": hash_password(password)} if db_mode != "firestore" else {}),
    }
    save_user(user_id, new_user)

    access_token = create_access_token(data={"sub": user_id, "email": email})
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        is_new_user=True
    )

@router.post("/email/login", response_model=AuthResponse, summary="E-posta ile giriş yap")
async def email_login(payload: EmailLoginRequest):
    """
    E-posta ve şifre ile giriş (Mock/Local veya Firebase Auth).
    """
    email = payload.email
    password = payload.password
    
    user_id = "usr_" + hashlib.md5(email.lower().encode()).hexdigest()[:12]
    
    db_mode = get_db_mode()
    if db_mode == "firestore":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase e-posta girişi için GOOGLE_API_KEY yapılandırılmalı.",
            )
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
                    json={"email": email, "password": password, "returnSecureToken": True},
                )
            if response.status_code != 200:
                raise ValueError("invalid credentials")
            user_id = response.json()["localId"]
        except (httpx.HTTPError, KeyError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-posta veya şifre hatalı."
            )
    else:
        user_profile = get_user(user_id)
        password_hash = user_profile.get("passwordHash") if user_profile else None
        if not password_hash or not verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-posta veya şifre hatalı.",
            )

    access_token = create_access_token(data={"sub": user_id, "email": email})
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        is_new_user=False
    )

def datetime_to_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
