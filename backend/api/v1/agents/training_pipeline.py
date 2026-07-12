"""
Training Pipeline – Tüm eğitim senaryolarını çalıştırır, kalite raporu üretir.
"""
from typing import Dict, Any, List
from api.v1.agents.training_data import TRAINING_SCENARIOS, evaluate_agent_output
from api.v1.agents.profile_analyzer_agent import analyze_user_profile
from api.v1.agents.financial_agent import analyze_finances
from api.v1.agents.career_coach_agent import create_career_roadmap
from api.v1.agents.wellbeing_agent import check_wellbeing
from api.v1.agents.migration_agent import create_migration_plan
from api.v1.agents.skill_gap_agent import analyze_skill_gaps
from api.v1.agents.timeline_agent import estimate_timeline


AGENT_FUNCTIONS = {
    "profile_analyzer": lambda up, pa, sn: analyze_user_profile(up),
    "financial": lambda up, pa, sn: analyze_finances(up, pa),
    "career_coach": lambda up, pa, sn: create_career_roadmap(up, pa, sn),
    "wellbeing": lambda up, pa, sn: check_wellbeing(up, pa),
    "migration": lambda up, pa, sn: create_migration_plan(up, pa),
    "skill_gap": lambda up, pa, sn: analyze_skill_gaps(up, pa, sn),
    "timeline": lambda up, pa, sn: estimate_timeline(up, pa),
}


def run_training_pipeline(scenario_ids: List[str] = None, agents_to_test: List[str] = None) -> Dict[str, Any]:
    """
    Eğitim senaryolarını çalıştırır ve her agent için kalite raporu üretir.
    """
    scenarios = TRAINING_SCENARIOS
    if scenario_ids:
        scenarios = [s for s in scenarios if s["scenario_id"] in scenario_ids]

    agents = agents_to_test or list(AGENT_FUNCTIONS.keys())

    all_results = []
    agent_scores: Dict[str, List[int]] = {a: [] for a in agents}
    scenario_summaries = []

    for scenario in scenarios:
        user_profile = scenario["user_profile"]
        scenario_result = {
            "scenario_id": scenario["scenario_id"],
            "scenario_name": scenario["name"],
            "archetype_expected": scenario["expected_archetype"],
            "agents_tested": [],
        }

        # Run ProfileAnalyzer first
        try:
            profile_analysis = analyze_user_profile(user_profile)
            archetype_match = profile_analysis.get("archetype") == scenario["expected_archetype"]
            scenario_result["archetype_detected"] = profile_analysis.get("archetype")
            scenario_result["archetype_match"] = archetype_match
        except Exception as e:
            profile_analysis = {"archetype": "Pratik", "risk_tolerance": "medium", "urgency_score": 5}
            scenario_result["archetype_error"] = str(e)

        # Run each agent
        for agent_name in agents:
            if agent_name not in AGENT_FUNCTIONS or agent_name == "profile_analyzer":
                continue
            try:
                output = AGENT_FUNCTIONS[agent_name](user_profile, profile_analysis, [])
                quality = evaluate_agent_output(scenario["scenario_id"], agent_name, output)
                agent_scores[agent_name].append(quality["score"])
                scenario_result["agents_tested"].append({
                    "agent": agent_name,
                    "score": quality["score"],
                    "keyword_hits": quality.get("keyword_hits", 0),
                    "total_keywords": quality.get("total_keywords", 0),
                    "source": output.get("source", "unknown"),
                })
            except Exception as e:
                agent_scores[agent_name].append(0)
                scenario_result["agents_tested"].append({"agent": agent_name, "score": 0, "error": str(e)})

        scenario_summaries.append(scenario_result)

    # Aggregate scores per agent
    agent_summary = {}
    for agent, scores in agent_scores.items():
        if scores:
            agent_summary[agent] = {
                "avg_score": round(sum(scores) / len(scores), 1),
                "min_score": min(scores),
                "max_score": max(scores),
                "total_runs": len(scores),
                "grade": "A" if sum(scores)/len(scores) >= 80 else "B" if sum(scores)/len(scores) >= 60 else "C" if sum(scores)/len(scores) >= 40 else "D",
            }

    overall_avg = round(sum(v["avg_score"] for v in agent_summary.values()) / max(1, len(agent_summary)), 1) if agent_summary else 0

    return {
        "pipeline_run_summary": {
            "scenarios_tested": len(scenario_summaries),
            "agents_tested": len(agents),
            "overall_score": overall_avg,
            "overall_grade": "A" if overall_avg >= 80 else "B" if overall_avg >= 60 else "C" if overall_avg >= 40 else "D",
        },
        "agent_performance": agent_summary,
        "scenario_results": scenario_summaries,
        "recommendations": _generate_recommendations(agent_summary),
    }


def _generate_recommendations(agent_summary: Dict) -> List[str]:
    recs = []
    for agent, stats in agent_summary.items():
        if stats["avg_score"] < 60:
            recs.append(f"⚠️ {agent}: Ortalama {stats['avg_score']} puan — prompt iyileştirmesi gerekli")
        elif stats["min_score"] < 40:
            recs.append(f"🔍 {agent}: Min puan {stats['min_score']} — belirli senaryolarda zayıflık var")
        else:
            recs.append(f"✅ {agent}: {stats['grade']} — {stats['avg_score']} ortalama puan ile iyi performans")
    return recs
