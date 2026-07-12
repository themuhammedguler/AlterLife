"""
OrchestratorAgent – Kullanıcıyı tanıyan ve tüm agent'ları yönlendiren merkezi beyin.

Akış:
1. Tüm kullanıcı verisini topla (profil, skills, library, simülasyon, analytics)
2. ProfileAnalyzerAgent'ı çalıştır → Kişilik arketipi + hangi agent'lar aktif olacak
3. Belirlenen agent'ları çalıştır
4. Sonuçları birleştir → "Günlük Yönlendirme Raporu" döner
"""

import os
from typing import Dict, Any, List, Optional
from datetime import date

from api.v1.database import (
    get_user, get_skills, get_library, get_daily_quests,
    get_simulation_tree, get_analytics_events, save_user
)
from api.v1.agents.profile_analyzer_agent import analyze_user_profile
from api.v1.agents.financial_agent import analyze_finances
from api.v1.agents.career_coach_agent import create_career_roadmap
from api.v1.agents.wellbeing_agent import check_wellbeing
from api.v1.agents.migration_agent import create_migration_plan
from api.v1.agents.skill_gap_agent import analyze_skill_gaps
from api.v1.agents.timeline_agent import estimate_timeline


# ── Agent Registry ────────────────────────────────────────────────────────────

AGENT_REGISTRY = {
    "financial": {"name": "FinancialAdvisorAgent", "emoji": "💰", "description": "Birikim planı ve finansal özgürlük tahmini"},
    "career_coach": {"name": "CareerCoachAgent", "emoji": "🗺️", "description": "Kişisel kariyer yol haritası ve skill gap analizi"},
    "wellbeing": {"name": "WellbeingAgent", "emoji": "🧘", "description": "Burnout riski ve iyileşme önerileri"},
    "migration": {"name": "MigrationAgent", "emoji": "✈️", "description": "Yurt dışı taşınma planlaması"},
    "skill_gap": {"name": "SkillGapAgent", "emoji": "📚", "description": "Kritik beceri boşluğu ve öğrenme sırası"},
    "timeline": {"name": "TimelineAgent", "emoji": "📅", "description": "Gerçekçi hedef tamamlama tahmini"},
    "scenario": {"name": "ScenarioAgent", "emoji": "🔮", "description": "Gelecek senaryosu simülasyonu"},
}

# ── Goal-based agent routing rules ───────────────────────────────────────────

def _rule_based_agents(goal: str, stress_level: int, monthly_savings: int) -> List[str]:
    """Hedef anahtar kelimelerine ve metriklerine göre zorunlu agent listesi döner."""
    goal_lower = goal.lower()
    agents = ["profile_analyzer"]  # Always first

    # Migration triggers
    if any(k in goal_lower for k in ["almanya", "kanada", "hollanda", "berlin", "yurt dışı", "göç", "vize", "master", "yüksek lisans"]):
        agents += ["migration", "financial", "career_coach", "skill_gap", "timeline"]

    # Startup/entrepreneurship
    elif any(k in goal_lower for k in ["startup", "girişim", "saas", "kendi işim", "freelance", "serbest"]):
        agents += ["financial", "career_coach", "timeline", "wellbeing"]

    # Career change
    elif any(k in goal_lower for k in ["kariyer geçiş", "pm", "product manager", "manager", "lider", "cto"]):
        agents += ["career_coach", "skill_gap", "timeline"]

    # Remote work
    elif any(k in goal_lower for k in ["uzaktan", "remote", "yabancı şirket"]):
        agents += ["career_coach", "skill_gap", "timeline", "financial"]

    # Wellbeing/burnout priority
    elif any(k in goal_lower for k in ["burnout", "anlam", "mola", "denge"]) or stress_level > 70:
        agents += ["wellbeing", "financial", "career_coach"]

    else:
        agents += ["career_coach", "skill_gap", "timeline", "financial"]

    # Always add wellbeing if stress is high
    if stress_level > 60 and "wellbeing" not in agents:
        agents.append("wellbeing")

    # Always add financial if savings are low
    if monthly_savings < 300 and "financial" not in agents:
        agents.append("financial")

    return agents


def _synthesize_daily_focus(profile_analysis: Dict, financial: Dict, career: Dict, wellbeing: Optional[Dict], timeline: Dict) -> Dict[str, Any]:
    """Tüm agent çıktılarından 'bugün ne yapmalıyım?' sentezi üretir."""
    archetype = profile_analysis.get("archetype", "Pratik")
    risk_level = wellbeing.get("risk_level", "Düşük") if wellbeing else "Düşük"

    today_focus = []
    next_30_days = []
    warnings = []
    opportunities = []

    # Today focus: combine quick wins from all agents
    if wellbeing and risk_level in ["Kritik", "Yüksek"]:
        today_focus.append(f"🧘 {wellbeing['recovery_recommendations'][0]['action']} (Sağlık öncelikli!)")

    if career and career.get("quick_start_action"):
        today_focus.append(f"🗺️ {career['quick_start_action']}")

    if financial and financial.get("quick_wins"):
        today_focus.append(f"💰 {financial['quick_wins'][0]}")

    # Next 30 days from career roadmap phases
    if career and career.get("roadmap_phases"):
        phase = career["roadmap_phases"][0]
        for m in (phase.get("milestones") or [])[:2]:
            next_30_days.append(m)

    # Warnings
    if wellbeing and risk_level in ["Kritik", "Yüksek"]:
        warnings.append(f"⚠️ Burnout risk: {risk_level} — {wellbeing.get('risk_explanation', '')}")
    if financial and financial.get("key_warnings"):
        warnings.append(f"💸 {financial['key_warnings'][0]}")

    # Opportunities
    if timeline and timeline.get("acceleration_tips"):
        opportunities.append(f"⚡ {timeline['acceleration_tips'][0]}")
    if career and career.get("job_market_insight"):
        opportunities.append(f"🎯 {career['job_market_insight']}")

    return {
        "today_focus": today_focus[:3],
        "next_30_days": next_30_days[:4],
        "warnings": warnings[:3],
        "opportunities": opportunities[:3],
    }


# ── Main Orchestration Function ───────────────────────────────────────────────

def orchestrate(user_id: str) -> Dict[str, Any]:
    """
    Kullanıcı ID'si alır, tüm veriyi toplar, agent'ları çalıştırır,
    kapsamlı bir yönlendirme raporu döner.
    """
    # 1. Veri toplama
    user_data = get_user(user_id) or {}
    skill_nodes = get_skills(user_id) or []
    library = get_library(user_id) or []
    quests = get_daily_quests(user_id) or []
    sim_tree = get_simulation_tree(f"sim_{user_id}") or {}
    analytics_events = get_analytics_events(user_id) or []

    # Enrich user profile with computed fields
    completed_quests = sum(1 for q in quests if q.get("status") == "completed")
    lib_completed = sum(1 for r in library if r.get("is_completed"))
    active_days = len({ev.get("date", "")[:10] for ev in analytics_events if ev.get("date")}) or max(1, user_data.get("level", 1))
    stress_level = user_data.get("stress_level", 40)
    monthly_savings = user_data.get("monthly_savings", 500)

    user_profile_data = user_data.get("profile", {})
    enriched_profile = {
        **user_data,
        **user_profile_data,
        "user_id": user_id,
        "completed_quests": completed_quests,
        "library_completed": lib_completed,
        "active_days": active_days,
        "stress_level": stress_level,
        "monthly_savings": monthly_savings,
        "field": user_profile_data.get("role", "Software Developer"),
        "known_skills": [n["name"] for n in skill_nodes if n.get("is_unlocked") and n.get("level", 0) >= 1],
    }

    goal = enriched_profile.get("freeGoal", enriched_profile.get("field", "kariyer gelişimi"))

    # 2. ProfileAnalyzer – merkezi beyin
    print(f"[Orchestrator] Running ProfileAnalyzerAgent for user {user_id}...")
    profile_analysis = analyze_user_profile(enriched_profile)

    # Persist the calculated archetype back to user database document
    if user_data:
        if "profile" not in user_data:
            user_data["profile"] = {}
        user_data["profile"]["archetype"] = profile_analysis.get("archetype", "Pratik")
        user_data["profile"]["archetype_description"] = profile_analysis.get("archetype_description", "")
        save_user(user_id, user_data)

    # 3. Rule-based routing + profile recommendations
    rule_agents = _rule_based_agents(goal, stress_level, monthly_savings)
    profile_recommended = profile_analysis.get("recommended_agents", [])
    activated_agents = list(dict.fromkeys(rule_agents + ["profile_analyzer"] + profile_recommended))  # deduplicate, preserve order

    print(f"[Orchestrator] Activated agents: {activated_agents}")

    # 4. Run each agent
    results = {}

    if "financial" in activated_agents:
        print("[Orchestrator] Running FinancialAdvisorAgent...")
        results["financial"] = analyze_finances(enriched_profile, profile_analysis)

    if "career_coach" in activated_agents:
        print("[Orchestrator] Running CareerCoachAgent...")
        results["career_coach"] = create_career_roadmap(enriched_profile, profile_analysis, skill_nodes)

    if "wellbeing" in activated_agents:
        print("[Orchestrator] Running WellbeingAgent...")
        results["wellbeing"] = check_wellbeing(enriched_profile, profile_analysis)

    if "migration" in activated_agents:
        print("[Orchestrator] Running MigrationAgent...")
        results["migration"] = create_migration_plan(enriched_profile, profile_analysis)

    if "skill_gap" in activated_agents:
        print("[Orchestrator] Running SkillGapAgent...")
        results["skill_gap"] = analyze_skill_gaps(enriched_profile, profile_analysis, skill_nodes)

    if "timeline" in activated_agents:
        print("[Orchestrator] Running TimelineAgent...")
        results["timeline"] = estimate_timeline(enriched_profile, profile_analysis, {"events": analytics_events})

    # 5. Synthesize daily focus
    unified_report = _synthesize_daily_focus(
        profile_analysis,
        results.get("financial", {}),
        results.get("career_coach", {}),
        results.get("wellbeing"),
        results.get("timeline", {}),
    )

    # 6. Build final response
    return {
        "user_id": user_id,
        "generated_at": str(date.today()),
        "user_archetype": profile_analysis.get("archetype", "Pratik"),
        "archetype_description": profile_analysis.get("archetype_description", ""),
        "risk_tolerance": profile_analysis.get("risk_tolerance", "medium"),
        "primary_goal": goal,
        "urgency_score": profile_analysis.get("urgency_score", 5),
        "motivational_message": profile_analysis.get("motivational_message", ""),
        "activated_agents": [a for a in activated_agents if a != "profile_analyzer"],
        "agent_descriptions": {k: AGENT_REGISTRY[k] for k in activated_agents if k in AGENT_REGISTRY},
        "profile_analysis": profile_analysis,
        "unified_report": unified_report,
        "agent_results": results,
        "profile_stats": {
            "level": enriched_profile.get("level", 1),
            "xp": enriched_profile.get("xp", 0),
            "completed_quests": completed_quests,
            "library_completed": lib_completed,
            "active_days": active_days,
            "skills_unlocked": len([n for n in skill_nodes if n.get("is_unlocked")]),
        },
    }
