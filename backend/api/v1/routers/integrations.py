"""
Integrations Router – /api/v1/integrations
Google Calendar ve GitHub OAuth bağlantı yönetimi
"""

import os
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, save_user

router = APIRouter(prefix="/integrations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class OAuthConnectRequest(BaseModel):
    code: str           # OAuth authorization code from frontend
    redirect_uri: str


class IntegrationStatus(BaseModel):
    service: str        # "google_calendar" | "github"
    is_connected: bool
    username: Optional[str] = None
    last_synced: Optional[str] = None


class CalendarQuestEventRequest(BaseModel):
    quest_id: str
    title: str
    description: Optional[str] = None
    time_slot: Optional[str] = None
    duration_minutes: int = 25


# ── Google Calendar ───────────────────────────────────────────────────────────

@router.post("/calendar/connect", summary="Google Calendar OAuth bağlantısı")
async def connect_calendar(payload: OAuthConnectRequest, user_id: str = Depends(get_current_user_id)):
    """
    Google Calendar OAuth 2.0 ile bağlantı kurar ve refresh token'ı saklar.
    """
    code = payload.code
    
    # Check for mock code for tests
    if code == "mock_code_calendar":
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            raise HTTPException(status_code=401, detail="Mock OAuth production ortamında kullanılamaz.")
        user_data = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@placeholder.com"}
        if "integrations" not in user_data:
            user_data["integrations"] = {}
        user_data["integrations"]["google_calendar"] = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "connected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "username": "mock_google_user@gmail.com"
        }
        save_user(user_id, user_data)
        return {"status": "connected", "service": "google_calendar"}
        
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar credentials (Client ID / Client Secret) are not set in environment."
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token"),
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": payload.redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google token exchange failed: {response.text}"
                )
                
            token_data = response.json()
            
            # Fetch user email / info from google
            userinfo_res = await client.get(
                os.getenv("GOOGLE_USERINFO_URL", "https://www.googleapis.com/oauth2/v2/userinfo"),
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            email = userinfo_res.json().get("email") if userinfo_res.status_code == 200 else "Connected Google Account"

            user_data = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@placeholder.com"}
            if "integrations" not in user_data:
                user_data["integrations"] = {}
                
            user_data["integrations"]["google_calendar"] = {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
                "connected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "username": email
            }
            save_user(user_id, user_data)
            return {"status": "connected", "service": "google_calendar"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google integration error: {str(e)}")


@router.get("/calendar/status", response_model=IntegrationStatus, summary="Calendar bağlantı durumu")
async def calendar_status(user_id: str = Depends(get_current_user_id)):
    user_data = get_user(user_id) or {}
    calendar_data = user_data.get("integrations", {}).get("google_calendar")
    
    if not calendar_data:
        return IntegrationStatus(service="google_calendar", is_connected=False)
        
    return IntegrationStatus(
        service="google_calendar",
        is_connected=True,
        username=calendar_data.get("username", "Connected Account"),
        last_synced=calendar_data.get("connected_at")
    )


@router.delete("/calendar", summary="Google Calendar bağlantısını kaldır")
async def disconnect_calendar(user_id: str = Depends(get_current_user_id)):
    user_data = get_user(user_id) or {}
    user_data.setdefault("integrations", {}).pop("google_calendar", None)
    save_user(user_id, user_data)
    return {"status": "disconnected", "service": "google_calendar"}


@router.post("/calendar/quest-event", summary="Görevi Google Calendar'a hatırlatma olarak ekle")
async def create_calendar_quest_event(
    payload: CalendarQuestEventRequest,
    user_id: str = Depends(get_current_user_id),
):
    user_data = get_user(user_id) or {}
    calendar_data = user_data.get("integrations", {}).get("google_calendar")
    if not calendar_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google Calendar bağlı değil.")

    slot_hours = {"Sabah": 9, "Öğle": 13, "Akşam": 19, "Gece": 21}
    start_hour = slot_hours.get(payload.time_slot or "Akşam", 19)
    start = datetime.now(timezone.utc).replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=payload.duration_minutes)

    event_body = {
        "summary": f"[AlterLife] {payload.title}",
        "description": payload.description or "AlterLife günlük quest hatırlatması.",
        "start": {"dateTime": start.isoformat().replace("+00:00", "Z")},
        "end": {"dateTime": end.isoformat().replace("+00:00", "Z")},
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]},
    }

    if calendar_data.get("access_token") == "mock_access_token":
        return {
            "status": "created",
            "event_id": f"mock_evt_{payload.quest_id}",
            "html_link": "https://calendar.google.com/calendar",
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {calendar_data.get('access_token')}"},
            json=event_body,
        )
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Calendar event oluşturulamadı.")
    data = response.json()
    return {"status": "created", "event_id": data.get("id"), "html_link": data.get("htmlLink")}


# ── GitHub ────────────────────────────────────────────────────────────────────

@router.post("/github/connect", summary="GitHub OAuth bağlantısı")
async def connect_github(payload: OAuthConnectRequest, user_id: str = Depends(get_current_user_id)):
    """
    GitHub OAuth ile bağlantı kurar ve kullanıcı adını saklar.
    """
    code = payload.code
    
    # Check for mock code for tests
    if code == "mock_code_github":
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            raise HTTPException(status_code=401, detail="Mock OAuth production ortamında kullanılamaz.")
        user_data = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@placeholder.com"}
        if "integrations" not in user_data:
            user_data["integrations"] = {}
        user_data["integrations"]["github"] = {
            "access_token": "mock_github_access_token",
            "connected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "username": "mock_github_user"
        }
        save_user(user_id, user_data)
        return {"status": "connected", "service": "github"}
        
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub credentials (Client ID / Client Secret) are not set in environment."
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("GITHUB_TOKEN_URL", "https://github.com/login/oauth/access_token"),
                headers={"Accept": "application/json"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": payload.redirect_uri
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub token exchange failed: {response.text}"
                )
                
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub login failed: {token_data.get('error_description', 'No access token received')}"
                )
                
            # Fetch user info
            user_res = await client.get(
                f"{os.getenv('GITHUB_API_URL', 'https://api.github.com').rstrip('/')}/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "User-Agent": "AlterLife-App"
                }
            )
            username = user_res.json().get("login") if user_res.status_code == 200 else "Connected GitHub User"

            user_data = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@placeholder.com"}
            if "integrations" not in user_data:
                user_data["integrations"] = {}
                
            user_data["integrations"]["github"] = {
                "access_token": access_token,
                "connected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "username": username
            }
            save_user(user_id, user_data)
            return {"status": "connected", "service": "github"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub integration error: {str(e)}")


@router.get("/github/status", response_model=IntegrationStatus, summary="GitHub bağlantı durumu")
async def github_status(user_id: str = Depends(get_current_user_id)):
    user_data = get_user(user_id) or {}
    github_data = user_data.get("integrations", {}).get("github")
    
    if not github_data:
        return IntegrationStatus(service="github", is_connected=False)
        
    return IntegrationStatus(
        service="github",
        is_connected=True,
        username=github_data.get("username", "Connected Account"),
        last_synced=github_data.get("connected_at")
    )


@router.delete("/github", summary="GitHub bağlantısını kaldır")
async def disconnect_github(user_id: str = Depends(get_current_user_id)):
    user_data = get_user(user_id) or {}
    user_data.setdefault("integrations", {}).pop("github", None)
    save_user(user_id, user_data)
    return {"status": "disconnected", "service": "github"}
