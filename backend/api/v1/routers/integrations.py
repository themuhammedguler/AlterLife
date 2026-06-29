"""
Integrations Router – /api/v1/integrations
Google Calendar ve GitHub OAuth bağlantı yönetimi
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/integrations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class OAuthConnectRequest(BaseModel):
    code: str           # OAuth authorization code from frontend
    redirect_uri: str


class IntegrationStatus(BaseModel):
    service: str        # "google_calendar" | "github"
    is_connected: bool
    username: Optional[str]
    last_synced: Optional[str]


# ── Google Calendar ───────────────────────────────────────────────────────────

@router.post("/calendar/connect", summary="Google Calendar OAuth bağlantısı")
async def connect_calendar(payload: OAuthConnectRequest):
    """
    Google Calendar OAuth 2.0 ile bağlantı kurar ve refresh token'ı saklar.
    TODO: Google OAuth token exchange – Hafta 3
    """
    raise HTTPException(status_code=501, detail="Google Calendar entegrasyonu Hafta 3'te eklenecek.")


@router.get("/calendar/status", response_model=IntegrationStatus, summary="Calendar bağlantı durumu")
async def calendar_status():
    return IntegrationStatus(service="google_calendar", is_connected=False, username=None, last_synced=None)


# ── GitHub ────────────────────────────────────────────────────────────────────

@router.post("/github/connect", summary="GitHub OAuth bağlantısı")
async def connect_github(payload: OAuthConnectRequest):
    """
    GitHub OAuth ile bağlantı kurar ve kullanıcı adını saklar.
    TODO: GitHub OAuth token exchange – Hafta 3
    """
    raise HTTPException(status_code=501, detail="GitHub entegrasyonu Hafta 3'te eklenecek.")


@router.get("/github/status", response_model=IntegrationStatus, summary="GitHub bağlantı durumu")
async def github_status():
    return IntegrationStatus(service="github", is_connected=False, username=None, last_synced=None)
