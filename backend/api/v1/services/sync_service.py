import os
import httpx
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from api.v1.database import (
    get_user,
    save_user,
    get_daily_quests,
    save_daily_quests,
    append_analytics_event
)

async def refresh_google_token(refresh_token: str) -> Optional[str]:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            if res.status_code == 200:
                return res.json().get("access_token")
    except Exception:
        pass
    return None

async def check_google_calendar_activity(user_id: str, quest_title: str) -> bool:
    """
    Checks if there is a calendar event with '[AlterLife]' and the quest title
    occurring today in the user's primary calendar.
    """
    user_data = get_user(user_id) or {}
    calendar_data = user_data.get("integrations", {}).get("google_calendar")
    if not calendar_data:
        return False

    # Mock support for testing
    if calendar_data.get("access_token") == "mock_access_token":
        # Mock active event matching quest_title
        return True

    access_token = calendar_data.get("access_token")
    refresh_token = calendar_data.get("refresh_token")

    async def fetch_events(token: str) -> Optional[List[Dict[str, Any]]]:
        today_start = datetime.combine(date.today(), datetime.min.time()).isoformat() + "Z"
        today_end = datetime.combine(date.today(), datetime.max.time()).isoformat() + "Z"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "timeMin": today_start,
                        "timeMax": today_end,
                        "singleEvents": True
                    }
                )
                if res.status_code == 200:
                    return res.json().get("items", [])
                elif res.status_code == 401: # unauthorized, try refreshing
                    return None
        except Exception:
            pass
        return []

    events = await fetch_events(access_token)
    if events is None and refresh_token: # token expired
        new_token = await refresh_google_token(refresh_token)
        if new_token:
            # Update token in DB
            calendar_data["access_token"] = new_token
            user_data["integrations"]["google_calendar"] = calendar_data
            save_user(user_id, user_data)
            events = await fetch_events(new_token) or []
        else:
            events = []

    for event in (events or []):
        summary = event.get("summary", "").lower()
        # Look for "[alterlife]" and quest title in summary
        if "[alterlife]" in summary and quest_title.lower() in summary:
            return True
    return False

async def check_github_commit_activity(user_id: str) -> bool:
    """
    Checks if there are GitHub PushEvents from the user today.
    """
    user_data = get_user(user_id) or {}
    github_data = user_data.get("integrations", {}).get("github")
    if not github_data:
        return False

    # Mock support for testing
    if github_data.get("access_token") == "mock_github_access_token":
        return True

    username = github_data.get("username")
    access_token = github_data.get("access_token")
    if not username:
        return False

    try:
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "AlterLife-App"}
            if access_token:
                headers["Authorization"] = f"token {access_token}"

            res = await client.get(
                f"https://api.github.com/users/{username}/events",
                headers=headers
            )
            if res.status_code == 200:
                events = res.json()
                today_str = str(date.today())
                for ev in events:
                    if ev.get("type") == "PushEvent" and ev.get("created_at", "").startswith(today_str):
                        return True
    except Exception:
        pass
    return False

async def sync_and_verify_quests(user_id: str) -> List[Dict[str, Any]]:
    """
    Scans Google Calendar and GitHub for pending quests and auto-verifies them.
    Returns the updated quest list.
    """
    quests = get_daily_quests(user_id)
    if not quests:
        return []

    updated = False
    github_checked = False
    has_github_commit = False

    for quest in quests:
        if quest.get("status") != "pending":
            continue

        verified = False
        verified_by = quest.get("verified_by", "manual")

        if verified_by == "calendar_sync":
            verified = await check_google_calendar_activity(user_id, quest.get("title", ""))
        elif verified_by == "github_commit":
            if not github_checked:
                has_github_commit = await check_github_commit_activity(user_id)
                github_checked = True
            verified = has_github_commit

        if verified:
            # Auto-complete quest
            quest["status"] = "completed"
            quest["completed_at"] = datetime.utcnow().isoformat() + "Z"
            updated = True
            
            # Award XP & Level Up handling (reused logic from quests router)
            user_data = get_user(user_id) or {"user_id": user_id, "level": 1, "xp": 0, "next_level_xp": 1000, "rpgState": {"level": 1, "xp": 0}}
            rpg_state = user_data.get("rpgState", {"level": 1, "xp": 0, "next_level_xp": 1000, "title": "Novice Seeker"})
            
            xp_reward = quest.get("xp_reward", 100)
            current_xp = rpg_state.get("xp", 0) + xp_reward
            level = rpg_state.get("level", 1)
            next_level_xp = rpg_state.get("next_level_xp", level * 1000)
            
            while current_xp >= next_level_xp:
                current_xp -= next_level_xp
                level += 1
                next_level_xp = level * 1000
                
            title = "Novice Seeker"
            if level == 2: title = "Simulation Apprentice"
            elif level == 3: title = "Reality Architect"
            elif level >= 4: title = "AlterLife Master"
            
            rpg_state.update({
                "level": level,
                "xp": current_xp,
                "next_level_xp": next_level_xp,
                "title": title
            })
            user_data["rpgState"] = rpg_state
            save_user(user_id, user_data)
            
            # Save analytics event
            append_analytics_event(user_id, {
                "event_id": f"evt_quest_{quest.get('quest_id')}",
                "type": "quest_complete",
                "details": {
                    "quest_id": quest.get("quest_id"),
                    "title": quest.get("title"),
                    "xp_earned": xp_reward,
                    "verified_by": verified_by
                }
            })

    if updated:
        save_daily_quests(user_id, quests)

    return quests
