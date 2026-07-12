"""
Analytics Router – /api/v1/analytics
Kullanıcının ilerleme analitikleri: XP geçmişi, karar etki analizi, streak
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, get_simulation_tree, get_daily_quests, get_analytics_events

router = APIRouter(prefix="/analytics")


# ── Schemas ───────────────────────────────────────────────────────────────────

class KPISummary(BaseModel):
    total_xp: int
    level: int
    completed_quests: int
    active_days: int
    goal_alignment: int          # % (0-100)
    simulation_branches: int
    library_resources_completed: int


class XPDataPoint(BaseModel):
    label: str                   # "Pzt", "Sal" etc. or date string
    xp: int


class DecisionImpact(BaseModel):
    branch_id: str
    decision_name: str
    happiness_delta: int
    savings_delta: int
    stress_delta: int
    career_score: int


class AnalyticsSummaryResponse(BaseModel):
    kpi: KPISummary
    xp_history: List[XPDataPoint]
    decision_impacts: List[DecisionImpact]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_xp_history(events: List[dict]) -> List[XPDataPoint]:
    """Build last-7-days XP history from events; fills gaps with 0."""
    today = date.today()
    day_buckets = {}
    for i in range(7):
        d = today - timedelta(days=6 - i)
        day_buckets[str(d)] = 0

    for ev in events:
        ev_date = ev.get("date", "")[:10]
        if ev_date in day_buckets:
            day_buckets[ev_date] += ev.get("xp", 0)

    day_labels = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    result = []
    for i, (date_str, xp) in enumerate(day_buckets.items()):
        d = date.fromisoformat(date_str)
        result.append(XPDataPoint(label=day_labels[d.weekday()], xp=xp))
    return result


def _build_mock_xp_history(base_xp: int) -> List[XPDataPoint]:
    """Generate plausible XP history when no events exist yet."""
    labels = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    daily = [max(0, base_xp // 14 + (i * 7)) for i in range(7)]
    return [XPDataPoint(label=l, xp=v) for l, v in zip(labels, daily)]


def _extract_decision_impacts(sim_tree: Optional[dict]) -> List[DecisionImpact]:
    if not sim_tree:
        return []
    nodes = sim_tree.get("nodes", [])
    impacts = []
    for node in nodes:
        if node.get("parent") and node.get("metrics"):
            m = node["metrics"]
            impacts.append(DecisionImpact(
                branch_id=node.get("node_id", "?"),
                decision_name=node.get("decision_name", "Karar"),
                happiness_delta=m.get("happiness", 0),
                savings_delta=m.get("savings", 0),
                stress_delta=m.get("stress", 0),
                career_score=m.get("career_score", 0),
            ))
    return impacts[:5]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=AnalyticsSummaryResponse, summary="Analitik özet")
async def get_analytics_summary(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının tüm ilerleme metriklerini, XP geçmişini ve karar etki analizini döner.
    """
    user = get_user(user_id) or {}
    level = user.get("level", 1)
    total_xp = user.get("xp", 0)

    # Quests
    quests = get_daily_quests(user_id)
    completed_quests = sum(1 for q in quests if q.get("status") == "completed")

    # Simulation tree
    sim_id = f"sim_{user_id}"
    sim_tree = get_simulation_tree(sim_id)
    branch_count = max(0, len(sim_tree.get("nodes", [])) - 1) if sim_tree else 0

    # Analytics events
    events = get_analytics_events(user_id)
    active_days = len({ev.get("date", "")[:10] for ev in events if ev.get("date")}) if events else max(1, level)

    # Goal alignment heuristic
    goal_alignment = min(100, 40 + (level * 5) + (completed_quests * 3))

    # Library
    from api.v1.database import get_library
    lib = get_library(user_id)
    lib_completed = sum(1 for r in lib if r.get("is_completed"))

    kpi = KPISummary(
        total_xp=total_xp,
        level=level,
        completed_quests=completed_quests,
        active_days=active_days,
        goal_alignment=goal_alignment,
        simulation_branches=branch_count,
        library_resources_completed=lib_completed,
    )

    xp_history = _build_xp_history(events) if events else _build_mock_xp_history(total_xp)
    decision_impacts = _extract_decision_impacts(sim_tree)

    return AnalyticsSummaryResponse(kpi=kpi, xp_history=xp_history, decision_impacts=decision_impacts)
