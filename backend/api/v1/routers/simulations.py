"""
Simulations Router – /api/v1/simulations
Dallanan Karar Ağacı ve "What If" Engine
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Any

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_simulation_tree, get_user
from api.v1.services.simulation_service import (
    generate_initial_tree_data,
    add_branch_node,
    inject_crisis
)

router = APIRouter(prefix="/simulations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SimulationGenerateRequest(BaseModel):
    target: str             # Örn: "2 yıl içinde Berlin'de Senior Cloud Engineer olmak"
    current_profile: Optional[dict] = None   # Kullanıcının mevcut profil verisi


class BranchRequest(BaseModel):
    parent_node_id: str     # Örn: "node_root"
    decision_text: str      # Örn: "Aşık olup kariyeri yavaşlatırsam ne olur?"


class NodeMetrics(BaseModel):
    monthly_savings: float
    stress_level: int       # 0-100
    happiness: int          # 0-100
    career_progress: int    # 0-100


class SimulationNode(BaseModel):
    node_id: str
    parent: Optional[str]
    decision_name: str
    metrics: NodeMetrics
    description: Optional[str]
    milestones: Optional[List[str]] = []


class SimulationTreeResponse(BaseModel):
    simulation_id: str
    user_id: str
    initial_target: str
    nodes: List[SimulationNode]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=SimulationTreeResponse, summary="Ana simülasyon dalını üret (LangGraph + Gemini)")
async def generate_simulation(payload: SimulationGenerateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının hedefine göre LangGraph Orchestrator aracılığıyla
    Gemini Search Grounding ile ana karar ağacı dalını oluşturur.
    """
    target = payload.target
    simulation_id = f"sim_{user_id}"
    
    # Load profile details if not passed
    profile_data = payload.current_profile
    if not profile_data:
        user_data = get_user(user_id)
        if user_data:
            profile_data = user_data.get("profile", {})
        else:
            profile_data = {}

    try:
        tree = generate_initial_tree_data(simulation_id, user_id, target, profile_data)
        return SimulationTreeResponse(
            simulation_id=tree["simulation_id"],
            user_id=tree["user_id"],
            initial_target=tree["initial_target"],
            nodes=[
                SimulationNode(
                    node_id=n["node_id"],
                    parent=n["parent"],
                    decision_name=n["decision_name"],
                    metrics=NodeMetrics(
                        monthly_savings=n["metrics"]["monthly_savings"],
                        stress_level=n["metrics"]["stress_level"],
                        happiness=n["metrics"]["happiness"],
                        career_progress=n["metrics"]["career_progress"]
                    ),
                    description=n["description"],
                    milestones=n.get("milestones", [])
                )
                for n in tree["nodes"]
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simülasyon oluşturma başarısız: {str(e)}"
        )


@router.post("/{simulation_id}/branch", response_model=SimulationNode, summary="'What If?' – Yeni dal üret")
async def create_branch(simulation_id: str, payload: BranchRequest, user_id: str = Depends(get_current_user_id)):
    """
    Mevcut bir karar düğümünden yeni bir 'What If' dalı türetir.
    Örn: "Aşık olursam ne olur?" → yeni node ve metrikler
    """
    try:
        node = add_branch_node(simulation_id, payload.parent_node_id, payload.decision_text)
        return SimulationNode(
            node_id=node["node_id"],
            parent=node["parent"],
            decision_name=node["decision_name"],
            metrics=NodeMetrics(
                monthly_savings=node["metrics"]["monthly_savings"],
                stress_level=node["metrics"]["stress_level"],
                happiness=node["metrics"]["happiness"],
                career_progress=node["metrics"]["career_progress"]
            ),
            description=node["description"],
            milestones=node.get("milestones", [])
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dallanma oluşturma başarısız: {str(e)}"
        )


@router.get("/{simulation_id}/tree", response_model=SimulationTreeResponse, summary="Karar ağacını getir")
async def get_tree(simulation_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının tüm karar ağacını JSON olarak döner (interaktif harita için).
    """
    tree = get_simulation_tree(simulation_id)
    if not tree:
        # Generate a default one on-the-fly to avoid empty page
        user_data = get_user(user_id)
        target = "2 yıl içinde Berlin'de Senior Cloud Engineer olmak"
        profile_data = {}
        if user_data:
            profile_data = user_data.get("profile", {})
            target = profile_data.get("freeGoal", target)
            
        tree = generate_initial_tree_data(simulation_id, user_id, target, profile_data)
        
    return SimulationTreeResponse(
        simulation_id=tree["simulation_id"],
        user_id=tree["user_id"],
        initial_target=tree["initial_target"],
        nodes=[
            SimulationNode(
                node_id=n["node_id"],
                parent=n["parent"],
                decision_name=n["decision_name"],
                metrics=NodeMetrics(
                    monthly_savings=n["metrics"]["monthly_savings"],
                    stress_level=n["metrics"]["stress_level"],
                    happiness=n["metrics"]["happiness"],
                    career_progress=n["metrics"]["career_progress"]
                ),
                description=n["description"],
                milestones=n.get("milestones", [])
            )
            for n in tree["nodes"]
        ]
    )


@router.post("/{simulation_id}/stress-test", response_model=SimulationNode, summary="Black Swan stres testi")
async def stress_test(simulation_id: str, node_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Seçili dal için kriz senaryosu çalıştırır (ekonomik kriz, sağlık sorunu vb.)
    """
    try:
        node = inject_crisis(simulation_id, node_id)
        return SimulationNode(
            node_id=node["node_id"],
            parent=node["parent"],
            decision_name=node["decision_name"],
            metrics=NodeMetrics(
                monthly_savings=node["metrics"]["monthly_savings"],
                stress_level=node["metrics"]["stress_level"],
                happiness=node["metrics"]["happiness"],
                career_progress=node["metrics"]["career_progress"]
            ),
            description=node["description"],
            milestones=node.get("milestones", [])
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stres testi başarısız: {str(e)}"
        )
