"""
Agents Router – /api/v1/agents
Tüm AI agent endpoint'leri
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, get_skills
from api.v1.agents.orchestrator_agent import orchestrate, AGENT_REGISTRY
from api.v1.agents.profile_analyzer_agent import analyze_user_profile
from api.v1.agents.financial_agent import analyze_finances
from api.v1.agents.career_coach_agent import create_career_roadmap
from api.v1.agents.wellbeing_agent import check_wellbeing
from api.v1.agents.migration_agent import create_migration_plan
from api.v1.agents.skill_gap_agent import analyze_skill_gaps
from api.v1.agents.timeline_agent import estimate_timeline
from api.v1.agents.training_pipeline import run_training_pipeline

router = APIRouter(prefix="/agents")


# ── Schemas ───────────────────────────────────────────────────────────────────

class TrainingRequest(BaseModel):
    scenario_ids: Optional[List[str]] = None
    agents_to_test: Optional[List[str]] = None


# ── Orchestrator ──────────────────────────────────────────────────────────────

@router.post("/orchestrate", summary="🧠 OrchestratorAgent – Kapsamlı yönlendirme raporu")
async def run_orchestrator(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcıyı derinlemesine tanıyarak tüm ilgili agent'ları devreye sokar.
    Kişilik arketipi, günlük odak, uyarılar ve fırsatları tek raporda döner.
    """
    result = orchestrate(user_id)
    return result


# ── Profile Analyzer ──────────────────────────────────────────────────────────

@router.get("/profile/analysis", summary="🔍 ProfileAnalyzerAgent – Kişilik arketipi ve motivasyon analizi")
async def run_profile_analyzer(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    skill_nodes = get_skills(user_id) or []
    user["known_skills"] = [n["name"] for n in skill_nodes if n.get("is_unlocked") and n.get("level", 0) >= 1]
    return analyze_user_profile(user)


# ── Financial Advisor ─────────────────────────────────────────────────────────

@router.post("/financial/analyze", summary="💰 FinancialAdvisorAgent – Birikim planı ve özgürlük tarihi")
async def run_financial_agent(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    profile_analysis = analyze_user_profile(user)
    return analyze_finances(user, profile_analysis)


# ── Career Coach ──────────────────────────────────────────────────────────────

@router.post("/career/roadmap", summary="🗺️ CareerCoachAgent – Kişisel kariyer yol haritası")
async def run_career_coach(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    skill_nodes = get_skills(user_id) or []
    profile_analysis = analyze_user_profile(user)
    return create_career_roadmap(user, profile_analysis, skill_nodes)


# ── Wellbeing ─────────────────────────────────────────────────────────────────

@router.post("/wellbeing/check", summary="🧘 WellbeingAgent – Burnout riski ve iyileşme önerileri")
async def run_wellbeing_agent(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    profile_analysis = analyze_user_profile(user)
    return check_wellbeing(user, profile_analysis)


# ── Migration ─────────────────────────────────────────────────────────────────

@router.post("/migration/plan", summary="✈️ MigrationAgent – Yurt dışı taşınma planlaması")
async def run_migration_agent(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    profile_analysis = analyze_user_profile(user)
    return create_migration_plan(user, profile_analysis)


# ── Skill Gap ─────────────────────────────────────────────────────────────────

@router.post("/skills/gap", summary="📚 SkillGapAgent – Kritik beceri boşluğu analizi")
async def run_skill_gap_agent(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    skill_nodes = get_skills(user_id) or []
    profile_analysis = analyze_user_profile(user)
    return analyze_skill_gaps(user, profile_analysis, skill_nodes)


# ── Timeline ──────────────────────────────────────────────────────────────────

@router.post("/timeline/estimate", summary="📅 TimelineAgent – Gerçekçi hedef tamamlama tahmini")
async def run_timeline_agent(user_id: str = Depends(get_current_user_id)):
    user = get_user(user_id) or {}
    profile_analysis = analyze_user_profile(user)
    return estimate_timeline(user, profile_analysis)


# ── Agent Listing ─────────────────────────────────────────────────────────────

@router.get("/list", summary="Mevcut tüm agent'ların listesi")
async def list_agents():
    """Sistemde kayıtlı tüm agent'ları listeler."""
    return {"agents": AGENT_REGISTRY, "total": len(AGENT_REGISTRY)}


# ── Training Pipeline ─────────────────────────────────────────────────────────

@router.post("/train", summary="🏋️ Training Pipeline – Agent kalite raporu üret")
async def run_training(payload: TrainingRequest, user_id: str = Depends(get_current_user_id)):
    """
    Eğitim senaryoları üzerinde tüm agent'ları çalıştırır ve kalite raporu döner.
    Yalnızca ilk çalıştırmada birkaç saniye sürebilir.
    """
    result = run_training_pipeline(
        scenario_ids=payload.scenario_ids,
        agents_to_test=payload.agents_to_test,
    )
    return result
