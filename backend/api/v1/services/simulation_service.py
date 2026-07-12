import os
import json
import uuid
import random
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

from api.v1.database import get_simulation_tree, save_simulation_tree, get_user
from api.v1.agents.training_data import get_scenario_by_profile

# State definition
class SimulationState(TypedDict):
    simulation_id: str
    user_id: str
    user_profile: Optional[Dict[str, Any]]
    target: str
    decision_text: Optional[str]
    parent_node_id: Optional[str]
    tree_data: Dict[str, Any]
    new_node: Optional[Dict[str, Any]]
    crisis_node: Optional[Dict[str, Any]]
    error: Optional[str]

# ── Gemini helper ─────────────────────────────────────────────────────────────

def _call_gemini_json(prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API Key not configured")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        generation_config = {
            "response_mime_type": "application/json"
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"[Gemini] API error: {e}")
        raise e

# ── LangGraph Node Functions ──────────────────────────────────────────────────

def generate_scenario_node(state: SimulationState) -> SimulationState:
    target = state["target"]
    user_profile = state.get("user_profile") or {}
    
    prompt = f"""
    Kullanıcı Profili:
    - Yaş: {user_profile.get('age', '?')}
    - Meslek: {user_profile.get('field', '?')}
    - Mevcut Beceriler: {user_profile.get('known_skills', [])}
    - Aylık Birikim: {user_profile.get('monthly_savings', 500)}
    - Hedef: "{target}"
    
    Create a detailed decision path roadmap for this user. Return a JSON object with:
    1. A list of 4 key milestones (title, description, and estimated duration in months) to achieve this goal.
    2. An initial starting description of where the user begins.
    3. 2 path_options that represent initial strategic choices.
    
    Format:
    {{
        "milestones": ["Milestone 1: ...", "Milestone 2: ...", "Milestone 3: ...", "Milestone 4: ..."],
        "starting_description": "Initial setup...",
        "path_options": [
            {{
                "decision_name": "Option A (High risk/reward)",
                "description": "Short explanation of this branch...",
                "metrics_modifier": {{ "savings": 500, "stress": 20, "happiness": 10, "career": 15 }}
            }},
            {{
                "decision_name": "Option B (Low risk/balanced)",
                "description": "Short explanation...",
                "metrics_modifier": {{ "savings": -200, "stress": -10, "happiness": 20, "career": 10 }}
            }}
        ]
    }}
    """
    system_instruction = "You are a professional RPG career simulator. Return ONLY valid JSON. Use Turkish."
    
    try:
        data = _call_gemini_json(prompt, system_instruction)
        state["tree_data"] = {
            "initial_target": target,
            "milestones": data.get("milestones", []),
            "starting_description": data.get("starting_description", "Başlangıç Noktası"),
            "path_options": data.get("path_options", [])
        }
    except Exception:
        print("[LangGraph] Falling back to Mock initial scenario from training_data")
        scenario = get_scenario_by_profile(user_profile)
        milestones = scenario.get("expected_milestones_keywords", [])
        milestones = [f"{m.capitalize()} odaklı gelişim" for m in milestones]
        if len(milestones) < 4:
            milestones += ["İleri seviye projeler", "Hedefe varış"]
            
        state["tree_data"] = {
            "initial_target": target,
            "milestones": milestones[:4],
            "starting_description": f"{scenario['name']} senaryosuna başlıyorsunuz. Mevcut mesleğiniz: {user_profile.get('field', 'Belirsiz')}.",
            "path_options": [
                {
                    "decision_name": "Hızlı ve Agresif İlerleme",
                    "description": "Riskçi yaklaşım. Tüm limitleri zorlayarak ilerle.",
                    "metrics_modifier": { "savings": 200, "stress": 40, "happiness": -15, "career": 30 }
                },
                {
                    "decision_name": "Planlı ve Dengeli İlerleme",
                    "description": "Planlayıcı yaklaşım. İş-yaşam dengesini koruyarak ilerle.",
                    "metrics_modifier": { "savings": -100, "stress": 10, "happiness": 20, "career": 15 }
                }
            ]
        }
        
    return state


def multi_projection_node(state: SimulationState) -> SimulationState:
    tree = state["tree_data"]
    
    root_node = {
        "node_id": "node_root",
        "parent": None,
        "decision_name": "Başlangıç Durumu",
        "metrics": {
            "monthly_savings": 500,
            "stress_level": 30,
            "happiness": 70,
            "career_progress": 20
        },
        "description": tree.get("starting_description", "Simülasyon başlangıcı."),
        "milestones": []
    }
    
    nodes = [root_node]
    options = tree.get("path_options", [])
    
    for i, opt in enumerate(options):
        modifier = opt.get("metrics_modifier", {})
        
        new_savings = max(0, root_node["metrics"]["monthly_savings"] + modifier.get("savings", 0))
        new_stress = min(100, max(0, root_node["metrics"]["stress_level"] + modifier.get("stress", 0)))
        new_happiness = min(100, max(0, root_node["metrics"]["happiness"] + modifier.get("happiness", 0)))
        new_career = min(100, max(0, root_node["metrics"]["career_progress"] + modifier.get("career", 0)))
        
        child_node = {
            "node_id": f"node_path_{i+1}",
            "parent": "node_root",
            "decision_name": opt.get("decision_name"),
            "metrics": {
                "monthly_savings": new_savings,
                "stress_level": new_stress,
                "happiness": new_happiness,
                "career_progress": new_career
            },
            "description": opt.get("description"),
            "milestones": [tree["milestones"][i]] if i < len(tree.get("milestones", [])) else []
        }
        nodes.append(child_node)
        
    state["tree_data"]["nodes"] = nodes
    return state


def generate_branch_node(state: SimulationState) -> SimulationState:
    decision_text = state["decision_text"]
    parent_node_id = state["parent_node_id"]
    simulation_id = state["simulation_id"]
    user_profile = state.get("user_profile") or {}
    
    tree = get_simulation_tree(simulation_id)
    if not tree:
        state["error"] = "Simulation tree not found"
        return state
        
    parent_node = next((n for n in tree.get("nodes", []) if n["node_id"] == parent_node_id), None)
    if not parent_node:
        state["error"] = f"Parent node {parent_node_id} not found"
        return state

    prompt = f"""
    The user is currently at this state:
    - State Name: "{parent_node['decision_name']}"
    - Description: "{parent_node.get('description', '')}"
    - Current Metrics: {json.dumps(parent_node['metrics'])}
    
    User Profile Context:
    - Target: {tree.get("initial_target")}
    - User Arketip (If known): {user_profile.get("archetype", "Unknown")}
    
    The user wants to make a new "What If" decision: "{decision_text}"
    
    Calculate realistic consequences. Output a JSON object:
    {{
        "decision_name": "Short Title",
        "description": "Detailed explanation...",
        "metrics_modifier": {{ "savings": 1200, "stress": 20, "happiness": -5, "career": 10 }},
        "milestones": ["Milestone 1...", "Milestone 2..."]
    }}
    """
    system_instruction = "You are a professional RPG career simulator. Return ONLY valid JSON in Turkish."
    
    try:
        data = _call_gemini_json(prompt, system_instruction)
    except Exception:
        print("[LangGraph] Falling back to Mock branch generation")
        data = {
            "decision_name": f"Karar: {decision_text[:30]}",
            "description": f"Verdiğiniz '{decision_text}' kararı ile yeni bir aşamaya geçtiniz. Hedef: {tree.get('initial_target')}",
            "metrics_modifier": { "savings": random.randint(-500, 500), "stress": random.randint(-15, 25), "happiness": random.randint(-10, 20), "career": random.randint(-5, 15) },
            "milestones": ["Yeni sürecin analizini yap", "Gerekli kaynakları topla"]
        }
            
    mod = data.get("metrics_modifier", {})
    new_savings = max(0, parent_node["metrics"]["monthly_savings"] + mod.get("savings", 0))
    new_stress = min(100, max(0, parent_node["metrics"]["stress_level"] + mod.get("stress", 0)))
    new_happiness = min(100, max(0, parent_node["metrics"]["happiness"] + mod.get("happiness", 0)))
    new_career = min(100, max(0, parent_node["metrics"]["career_progress"] + mod.get("career", 0)))
    
    new_node = {
        "node_id": f"node_whatif_{uuid.uuid4().hex[:6]}",
        "parent": parent_node_id,
        "decision_name": data.get("decision_name", "Yeni Karar"),
        "metrics": {
            "monthly_savings": new_savings,
            "stress_level": new_stress,
            "happiness": new_happiness,
            "career_progress": new_career
        },
        "description": data.get("description"),
        "milestones": data.get("milestones", [])
    }
    
    tree["nodes"].append(new_node)
    save_simulation_tree(simulation_id, tree)
    
    state["tree_data"] = tree
    state["new_node"] = new_node
    return state


def black_swan_crisis_node(state: SimulationState) -> SimulationState:
    simulation_id = state["simulation_id"]
    parent_node_id = state["parent_node_id"]
    user_profile = state.get("user_profile") or {}
    
    tree = get_simulation_tree(simulation_id)
    if not tree:
        state["error"] = "Simulation tree not found"
        return state
        
    parent_node = next((n for n in tree.get("nodes", []) if n["node_id"] == parent_node_id), None)
    if not parent_node:
        state["error"] = f"Parent node {parent_node_id} not found"
        return state

    prompt = f"""
    The user is currently at this state:
    - State Name: "{parent_node['decision_name']}"
    - Current Metrics: {json.dumps(parent_node['metrics'])}
    - Target: {tree.get("initial_target")}
    - Profession: {user_profile.get("field", "Unknown")}
    
    Generate a Black Swan (unexpected crisis event) suited for this career path.
    Format:
    {{
        "crisis_title": "Crisis Warning!",
        "description": "Detailed explanation...",
        "metrics_modifier": {{ "savings": -1500, "stress": 35, "happiness": -20, "career": -15 }},
        "recovery_milestones": ["Action 1...", "Action 2..."]
    }}
    """
    system_instruction = "You are an RPG Black Swan Crisis Simulator. Return ONLY valid JSON in Turkish."
    
    try:
        data = _call_gemini_json(prompt, system_instruction)
    except Exception:
        print("[LangGraph] Falling back to Mock crisis event")
        
        target = tree.get("initial_target", "").lower()
        if "startup" in target or "girişim" in target:
            title, desc = "📉 Yatırım İptali", "Ana yatırımcınız son dakika anlaşmadan çekildi. Nakit akışı durdu."
            mm = {"savings": -2000, "stress": 50, "happiness": -30, "career": -10}
        elif "yurt dışı" in target or "almanya" in target:
            title, desc = "🛑 Vize Reddi / Gecikme", "Bürokratik sorunlar nedeniyle göç planınız 6 ay ertelendi."
            mm = {"savings": -500, "stress": 30, "happiness": -25, "career": -15}
        else:
            title, desc = "⚠️ Global Sektör Daralması", "Çalıştığınız sektörde ani bir daralma yaşandı."
            mm = {"savings": -800, "stress": 40, "happiness": -20, "career": -20}
            
        data = {
            "crisis_title": title,
            "description": desc,
            "metrics_modifier": mm,
            "recovery_milestones": ["Kriz eylem planını devreye sok", "Acil fonları kullan ve bütçeyi daralt"]
        }
        
    mod = data.get("metrics_modifier", {})
    new_savings = max(0, parent_node["metrics"]["monthly_savings"] + mod.get("savings", 0))
    new_stress = min(100, max(0, parent_node["metrics"]["stress_level"] + mod.get("stress", 0)))
    new_happiness = min(100, max(0, parent_node["metrics"]["happiness"] + mod.get("happiness", 0)))
    new_career = min(100, max(0, parent_node["metrics"]["career_progress"] + mod.get("career", 0)))
    
    crisis_node = {
        "node_id": f"node_crisis_{uuid.uuid4().hex[:6]}",
        "parent": parent_node_id,
        "decision_name": data.get("crisis_title", "Kara Kuğu Olayı"),
        "metrics": {
            "monthly_savings": new_savings,
            "stress_level": new_stress,
            "happiness": new_happiness,
            "career_progress": new_career
        },
        "description": data.get("description"),
        "milestones": data.get("recovery_milestones", [])
    }
    
    tree["nodes"].append(crisis_node)
    save_simulation_tree(simulation_id, tree)
    
    state["tree_data"] = tree
    state["crisis_node"] = crisis_node
    return state

# ── LangGraph Workflows ───────────────────────────────────────────────────────

def build_initial_tree_workflow():
    workflow = StateGraph(SimulationState)
    workflow.add_node("scenario", generate_scenario_node)
    workflow.add_node("projections", multi_projection_node)
    workflow.set_entry_point("scenario")
    workflow.add_edge("scenario", "projections")
    workflow.add_edge("projections", END)
    return workflow.compile()

def build_branch_workflow():
    workflow = StateGraph(SimulationState)
    workflow.add_node("branch", generate_branch_node)
    workflow.set_entry_point("branch")
    workflow.add_edge("branch", END)
    return workflow.compile()

def build_crisis_workflow():
    workflow = StateGraph(SimulationState)
    workflow.add_node("crisis", black_swan_crisis_node)
    workflow.set_entry_point("crisis")
    workflow.add_edge("crisis", END)
    return workflow.compile()

initial_tree_app = build_initial_tree_workflow()
branch_app = build_branch_workflow()
crisis_app = build_crisis_workflow()

# ── Service Wrapper Functions ─────────────────────────────────────────────────

def generate_initial_tree_data(simulation_id: str, user_id: str, target: str, profile_data: dict) -> Dict[str, Any]:
    initial_state = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "user_profile": profile_data,
        "target": target,
        "decision_text": None,
        "parent_node_id": None,
        "tree_data": {},
        "new_node": None,
        "crisis_node": None,
        "error": None
    }
    
    result = initial_tree_app.invoke(initial_state)
    final_tree = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "initial_target": target,
        "nodes": result["tree_data"]["nodes"]
    }
    save_simulation_tree(simulation_id, final_tree)
    return final_tree


def add_branch_node(simulation_id: str, parent_node_id: str, decision_text: str) -> Dict[str, Any]:
    tree = get_simulation_tree(simulation_id)
    user_id = tree.get("user_id", "") if tree else ""
    user_doc = get_user(user_id) if user_id else {}
    user_profile = {}
    if user_doc:
        user_profile = {
            **user_doc,
            **user_doc.get("profile", {}),
            "field": user_doc.get("profile", {}).get("role", "Software Developer")
        }
    
    initial_state = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "user_profile": user_profile,
        "target": tree.get("initial_target", "") if tree else "",
        "decision_text": decision_text,
        "parent_node_id": parent_node_id,
        "tree_data": {},
        "new_node": None,
        "crisis_node": None,
        "error": None
    }
    
    result = branch_app.invoke(initial_state)
    if result.get("error"):
        raise ValueError(result["error"])
    return result["new_node"]


def inject_crisis(simulation_id: str, parent_node_id: str) -> Dict[str, Any]:
    tree = get_simulation_tree(simulation_id)
    user_id = tree.get("user_id", "") if tree else ""
    user_doc = get_user(user_id) if user_id else {}
    user_profile = {}
    if user_doc:
        user_profile = {
            **user_doc,
            **user_doc.get("profile", {}),
            "field": user_doc.get("profile", {}).get("role", "Software Developer")
        }
    
    initial_state = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "user_profile": user_profile,
        "target": tree.get("initial_target", "") if tree else "",
        "decision_text": None,
        "parent_node_id": parent_node_id,
        "tree_data": {},
        "new_node": None,
        "crisis_node": None,
        "error": None
    }
    
    result = crisis_app.invoke(initial_state)
    if result.get("error"):
        raise ValueError(result["error"])
    return result["crisis_node"]
