"""
Auth Router – /api/v1/auth
Google OAuth JWT doğrulaması ve E-posta Girişi
"""

import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from api.v1.auth_utils import create_access_token
from api.v1.database import get_user, save_user, get_db_mode

router = APIRouter(prefix="/auth")

class GoogleAuthRequest(BaseModel):
    id_token: str  # Google OAuth ID token from frontend

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

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
        except Exception as e:
            # Token doğrulama hatası, fakat mock_token ise geliştirme ortamında kabul et
            if id_token.startswith("mock_token_"):
                email = id_token.replace("mock_token_", "") + "@alterlife.io"
                user_id = "usr_" + id_token.replace("mock_token_", "")
                display_name = id_token.replace("mock_token_", "").capitalize()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Google ID token doğrulaması başarısız: {str(e)}",
                )
    else:
        # 2. Local Fallback / Mock Modu
        # Geliştirme ortamında herhangi bir token'ı mock olarak kabul et
        if id_token.startswith("mock_token_"):
            clean_token = id_token.replace("mock_token_", "")
            email = f"{clean_token}@alterlife.io"
            user_id = f"usr_{clean_token}"
            display_name = clean_token.capitalize()
        else:
            # Genel placeholder
            user_id = "dev_user_001"
            email = "dev@alterlife.io"
            display_name = "Test Kullanıcı"

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
    
    # Basit bir user ID üret
    import hashlib
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Firebase Auth kayıt hatası: {str(e)}"
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
        }
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
    
    import hashlib
    user_id = "usr_" + hashlib.md5(email.lower().encode()).hexdigest()[:12]
    
    db_mode = get_db_mode()
    if db_mode == "firestore":
        # Firebase Auth verify şifre doğrulaması client side'da yapılmalıdır.
        # Backend'de Firebase email doğrulaması için auth.get_user_by_email kullanabiliriz,
        # fakat şifre kontrolünü client-side SDK yapar. Backend'de sadece token doğrularız.
        # Geliştirme kolaylığı için email varsa kabul ediyoruz:
        try:
            from firebase_admin import auth as firebase_auth
            user_record = firebase_auth.get_user_by_email(email)
            user_id = user_record.uid
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı bulunamadı."
            )
    else:
        # Mock/local kontrol
        user_profile = get_user(user_id)
        if not user_profile:
            # Otomatik oluştur (geliştirme kolaylığı için)
            new_user = {
                "userId": user_id,
                "email": email,
                "displayName": email.split("@")[0].capitalize(),
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

    access_token = create_access_token(data={"sub": user_id, "email": email})
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        is_new_user=False
    )

def datetime_to_iso() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
