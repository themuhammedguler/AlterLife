"""
Coach Router – /api/v1/coach
Active goal, weekly review, risk radar, mentor chat, decision journal,
milestone timeline, and reality check.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_daily_quests, get_simulation_tree, get_user, save_user
from api.v1.services.research_service import search_live_resources

router = APIRouter(prefix="/coach")


class ActiveGoalRequest(BaseModel):
    simulation_id: str = Field(min_length=3, max_length=160)
    node_id: str = Field(min_length=1, max_length=160)


class WeeklyReviewRequest(BaseModel):
    wins: List[str] = Field(default_factory=list, max_length=10)
    blockers: List[str] = Field(default_factory=list, max_length=10)
    energy_score: int = Field(default=70, ge=0, le=100)
    next_week_focus: Optional[str] = Field(default=None, max_length=240)


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    tone: str = Field(default="friendly", pattern="^(friendly|strict|playful)$")


class DecisionJournalRequest(BaseModel):
    decision: str = Field(min_length=3, max_length=400)
    expectation: str = Field(min_length=3, max_length=1000)
    confidence: int = Field(default=60, ge=0, le=100)
    revisit_in_days: int = Field(default=30, ge=1, le=365)


class NotificationReadRequest(BaseModel):
    notification_id: str = Field(min_length=3, max_length=120)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _active_goal(user_id: str) -> Dict[str, Any]:
    user = get_user(user_id) or {}
    goal = user.get("activeGoal")
    if goal:
        return goal

    tree = get_simulation_tree(f"sim_{user_id}")
    if tree and tree.get("nodes"):
        node = tree["nodes"][-1]
        return {
            "simulation_id": tree["simulation_id"],
            "node_id": node["node_id"],
            "title": node["decision_name"],
            "description": node.get("description", ""),
            "selected_at": None,
        }
    return {
        "simulation_id": f"sim_{user_id}",
        "node_id": "node_root",
        "title": "İlk hedefini seç",
        "description": "Simülasyon sayfasından bir dal seçerek ana hedefini sabitle.",
        "selected_at": None,
    }


def _risk_radar(user_id: str) -> Dict[str, Any]:
    goal = _active_goal(user_id)
    quests = get_daily_quests(user_id)
    completed = sum(1 for quest in quests if quest.get("status") == "completed")
    completion = completed / max(len(quests), 1)
    user = get_user(user_id) or {}
    energy = user.get("rpgState", {}).get("energy", 75)
    focus = user.get("rpgState", {}).get("focus", 75)
    title = goal.get("title", "").lower()

    risks = [
        {
            "name": "Zaman Riski",
            "score": max(10, min(95, round(75 - completion * 45))),
            "signal": "Quest tamamlanma ritmine göre ölçüldü.",
            "preventive_quest": "Bugün 20 dakikalık tek bir odak bloğu kilitle.",
        },
        {
            "name": "Enerji Riski",
            "score": max(5, min(95, 100 - energy)),
            "signal": "RPG energy durumundan hesaplandı.",
            "preventive_quest": "Ağır görevi böl, düşük enerji için mini quest seç.",
        },
        {
            "name": "Beceri Açığı",
            "score": 62 if any(word in title for word in ("cloud", "aws", "engineer", "devops")) else 45,
            "signal": "Aktif hedefin gerektirdiği beceri yoğunluğuna göre.",
            "preventive_quest": "Bir kaynak tamamla ve öğrendiğini portfolyo kanıtına çevir.",
        },
        {
            "name": "Gerçeklik Riski",
            "score": 68 if any(word in title for word in ("almanya", "germany", "master")) else 48,
            "signal": "Dış koşullar, belge, bütçe ve başvuru bağımlılıkları.",
            "preventive_quest": "Resmi kaynaklardan bir gereksinimi doğrula.",
        },
        {
            "name": "Odak Dağılması",
            "score": max(8, min(95, 100 - focus)),
            "signal": "Focus puanı ve rota sayısı birlikte değerlendirildi.",
            "preventive_quest": "Bugünün tek ana çıktısını yaz ve diğerlerini park et.",
        },
    ]
    return {"active_goal": goal, "risks": risks, "overall_risk": round(sum(r["score"] for r in risks) / len(risks))}


def _notifications(user_id: str) -> List[Dict[str, Any]]:
    goal = _active_goal(user_id)
    radar = _risk_radar(user_id)
    quests = get_daily_quests(user_id)
    completed = sum(1 for quest in quests if quest.get("status") == "completed")
    user = get_user(user_id) or {}
    read_ids = set(user.get("readNotifications", []))
    items = [
        {
            "notification_id": "notif_active_goal",
            "type": "goal",
            "title": "Aktif hedef hazır",
            "message": f"Şu an ana rota: {goal.get('title')}. Bugünün questlerini bu hedefe bağlayabilirsin.",
            "severity": "info",
            "created_at": goal.get("selected_at") or _now(),
        },
        {
            "notification_id": "notif_risk_radar",
            "type": "risk",
            "title": "Risk radar kontrolü",
            "message": f"Genel risk %{radar['overall_risk']}. En iyi önleyici hamle: {radar['risks'][0]['preventive_quest']}",
            "severity": "warning" if radar["overall_risk"] >= 60 else "info",
            "created_at": _now(),
        },
        {
            "notification_id": "notif_quest_progress",
            "type": "quest",
            "title": "Günlük quest ritmi",
            "message": f"Bugün {completed}/{len(quests) or 3} quest tamamlandı. Küçük bir hamle daha zinciri güçlendirir.",
            "severity": "success" if completed >= max(len(quests), 1) else "info",
            "created_at": _now(),
        },
        {
            "notification_id": "notif_weekly_review",
            "type": "review",
            "title": "Haftalık review zamanı",
            "message": "Haftayı kapatmak için Coach Center'da review oluştur.",
            "severity": "info",
            "created_at": _now(),
        },
    ]
    return [{**item, "is_read": item["notification_id"] in read_ids} for item in items]


def _report_markdown(user_id: str) -> str:
    goal = _active_goal(user_id)
    radar = _risk_radar(user_id)
    timeline = milestone_timeline_sync(user_id)
    quests = get_daily_quests(user_id)
    resources = search_live_resources(goal.get("title", "AlterLife hedef raporu"), 3)
    risk_lines = "\n".join(f"- {risk['name']}: %{risk['score']} — {risk['preventive_quest']}" for risk in radar["risks"])
    timeline_lines = "\n".join(f"- {item['period']}: {item['title']} — {item['output']}" for item in timeline["milestones"])
    quest_lines = "\n".join(f"- {quest.get('title')} (+{quest.get('xp_reward', 0)} XP)" for quest in quests[:5]) or "- Henüz quest yok"
    resource_lines = "\n".join(f"- [{item['title']}]({item['url']}) — {item['snippet']}" for item in resources)
    return f"""# AlterLife Hedef Raporu

## Aktif Hedef
{goal.get('title')}

{goal.get('description', '')}

## Reality Check
{reality_check_sync(user_id)['verdict']}

## Risk Radar
Genel risk: %{radar['overall_risk']}

{risk_lines}

## Milestone Timeline
{timeline_lines}

## Günlük Questler
{quest_lines}

## Kaynaklar
{resource_lines}
"""


def milestone_timeline_sync(user_id: str) -> Dict[str, Any]:
    goal = _active_goal(user_id)
    return {
        "active_goal": goal,
        "milestones": [
            {"period": "0-2 hafta", "title": "Netleştirme", "output": "Hedef kriterleri ve kaynak listesi"},
            {"period": "3-6 hafta", "title": "Kanıt üretimi", "output": "Portfolyo, CV, başvuru veya çalışma çıktısı"},
            {"period": "2-3 ay", "title": "Dış dünya testi", "output": "İlan, okul, mentor veya topluluk geri bildirimi"},
            {"period": "3-6 ay", "title": "Ana başvuru/hamle", "output": "Başvuru, görüşme, sertifika veya taşınma hazırlığı"},
            {"period": "6-12 ay", "title": "Dallanma kararı", "output": "Çalışma, master, remote veya alternatif rota seçimi"},
        ],
    }


def reality_check_sync(user_id: str) -> Dict[str, Any]:
    goal = _active_goal(user_id)
    user = get_user(user_id) or {}
    minutes = user.get("dailyPreferences", {}).get("available_minutes", 60)
    if minutes < 45:
        verdict = "Bu hedef olur, ama zaman çizelgesi uzar. 6 ay hayali yerine 12-18 ay gerçekçi."
    elif minutes < 90:
        verdict = "Gerçekçi. Haftalık review ile ritim korunursa güçlü ilerler."
    else:
        verdict = "Agresif ama mümkün. Tükenmemek için risk radarını haftalık kontrol et."
    return {
        "active_goal": goal,
        "verdict": verdict,
        "honest_constraint": "Sonuç, niyet kadar ayrılan düzenli zamana bağlı.",
        "minimum_weekly_commitment": "3 odak bloğu + 1 review",
    }


@router.get("/active-goal")
async def get_active_goal(user_id: str = Depends(get_current_user_id)):
    return _active_goal(user_id)


@router.post("/active-goal")
async def set_active_goal(payload: ActiveGoalRequest, user_id: str = Depends(get_current_user_id)):
    if payload.simulation_id != f"sim_{user_id}":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu simülasyon size ait değil.")
    tree = get_simulation_tree(payload.simulation_id)
    if not tree:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simülasyon bulunamadı.")
    node = next((item for item in tree.get("nodes", []) if item["node_id"] == payload.node_id), None)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dal bulunamadı.")
    user = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@alterlife.io"}
    user["activeGoal"] = {
        "simulation_id": payload.simulation_id,
        "node_id": payload.node_id,
        "title": node["decision_name"],
        "description": node.get("description", ""),
        "selected_at": _now(),
    }
    save_user(user_id, user)
    return user["activeGoal"]


@router.get("/risk-radar")
async def risk_radar(user_id: str = Depends(get_current_user_id)):
    return _risk_radar(user_id)


@router.post("/weekly-review")
async def weekly_review(payload: WeeklyReviewRequest, user_id: str = Depends(get_current_user_id)):
    radar = _risk_radar(user_id)
    focus = payload.next_week_focus or radar["risks"][0]["preventive_quest"]
    review = {
        "review_id": f"rev_{uuid.uuid4().hex[:8]}",
        "created_at": _now(),
        "summary": f"Bu hafta {len(payload.wins)} kazanım, {len(payload.blockers)} engel kaydedildi. Enerji skoru {payload.energy_score}/100.",
        "next_week_focus": focus,
        "recommended_adjustment": "Planı küçült ama zinciri kırma." if payload.energy_score < 45 else "Ana hedefi koru ve bir zor görevi öne al.",
        "risk_snapshot": radar["overall_risk"],
    }
    user = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@alterlife.io"}
    user.setdefault("weeklyReviews", []).append(review)
    save_user(user_id, user)
    return review


@router.post("/mentor/chat")
async def mentor_chat(payload: MentorChatRequest, user_id: str = Depends(get_current_user_id)):
    goal = _active_goal(user_id)
    radar = _risk_radar(user_id)
    prefix = {
        "friendly": "Sakin ilerleyelim:",
        "strict": "Gerçekçi konuşalım:",
        "playful": "Quest master modu:",
    }[payload.tone]
    resources = search_live_resources(f"{goal['title']} {payload.message}", 2)
    return {
        "answer": (
            f"{prefix} '{goal['title']}' hedefinde şu an ana risk %{radar['overall_risk']}. "
            f"Bugün tek hamle seç: {radar['risks'][0]['preventive_quest']} "
            "Sonra 10 dakika sonuç notu bırak."
        ),
        "suggested_action": radar["risks"][0]["preventive_quest"],
        "resources": resources,
    }


@router.post("/decision-journal")
async def add_decision_journal(payload: DecisionJournalRequest, user_id: str = Depends(get_current_user_id)):
    entry = {
        "entry_id": f"dec_{uuid.uuid4().hex[:8]}",
        "created_at": _now(),
        "decision": payload.decision,
        "expectation": payload.expectation,
        "confidence": payload.confidence,
        "revisit_in_days": payload.revisit_in_days,
        "status": "open",
    }
    user = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@alterlife.io"}
    user.setdefault("decisionJournal", []).append(entry)
    save_user(user_id, user)
    return entry


@router.get("/decision-journal")
async def list_decision_journal(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    return {"entries": user.get("decisionJournal", [])}


@router.get("/timeline")
async def milestone_timeline(user_id: str = Depends(get_current_user_id)):
    return milestone_timeline_sync(user_id)


@router.get("/reality-check")
async def reality_check(user_id: str = Depends(get_current_user_id)):
    return reality_check_sync(user_id)


@router.get("/report")
async def export_report(user_id: str = Depends(get_current_user_id)):
    markdown = _report_markdown(user_id)
    return {
        "filename": "alterlife-hedef-raporu.md",
        "format": "markdown",
        "markdown": markdown,
        "share_summary": markdown.split("\n\n")[0:4],
    }


@router.get("/notifications")
async def notification_center(user_id: str = Depends(get_current_user_id)):
    items = _notifications(user_id)
    return {
        "notifications": items,
        "unread_count": sum(1 for item in items if not item["is_read"]),
    }


@router.post("/notifications/read")
async def mark_notification_read(payload: NotificationReadRequest, user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {"userId": user_id, "email": f"{user_id}@alterlife.io"}
    read_ids = set(user.get("readNotifications", []))
    read_ids.add(payload.notification_id)
    user["readNotifications"] = sorted(read_ids)
    save_user(user_id, user)
    return {"status": "read", "notification_id": payload.notification_id}
