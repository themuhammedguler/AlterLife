"""
Simulations Router – /api/v1/simulations
Dallanan Karar Ağacı ve "What If" Engine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any

router = APIRouter(prefix="/simulations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SimulationGenerateRequest(BaseModel):
    target: str             # Örn: "2 yıl içinde Berlin'de Senior Cloud Engineer olmak"
    current_profile: dict   # Kullanıcının mevcut profil verisi


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

@router.post("/generate", summary="Ana simülasyon dalını üret (LangGraph + Gemini)")
async def generate_simulation(payload: SimulationGenerateRequest):
    """
    Kullanıcının hedefine göre LangGraph Orchestrator aracılığıyla
    Gemini Search Grounding ile ana karar ağacı dalını oluşturur.
    TODO: LangGraph SimulationAgent entegrasyonu – Hafta 2
    """
    raise HTTPException(status_code=501, detail="Hafta 2'de LangGraph ile implement edilecek.")


@router.post("/{simulation_id}/branch", summary="'What If?' – Yeni dal üret")
async def create_branch(simulation_id: str, payload: BranchRequest):
    """
    Mevcut bir karar düğümünden yeni bir 'What If' dalı türetir.
    Örn: "Aşık olursam ne olur?" → yeni node ve metrikler
    TODO: LangGraph BranchDecider + Gemini – Hafta 2
    """
    raise HTTPException(status_code=501, detail="Hafta 2'de implement edilecek.")


@router.get("/{simulation_id}/tree", response_model=SimulationTreeResponse, summary="Karar ağacını getir")
async def get_simulation_tree(simulation_id: str):
    """
    Kullanıcının tüm karar ağacını JSON olarak döner (interaktif harita için).
    TODO: Firestore'dan tree yükle – Hafta 2
    """
    # Placeholder – geliştirme için örnek veri
    return SimulationTreeResponse(
        simulation_id=simulation_id,
        user_id="dev_user_001",
        initial_target="2 yıl içinde Berlin'de Senior Cloud Engineer olmak",
        nodes=[
            SimulationNode(
                node_id="node_root",
                parent=None,
                decision_name="Başlangıç Durumu",
                metrics=NodeMetrics(
                    monthly_savings=500,
                    stress_level=30,
                    happiness=70,
                    career_progress=20,
                ),
                description="Türkiye'de yazılım geliştirici olarak çalışıyorsunuz.",
            ),
            SimulationNode(
                node_id="node_germany",
                parent="node_root",
                decision_name="Almanya'ya Taşınmak",
                metrics=NodeMetrics(
                    monthly_savings=3300,
                    stress_level=60,
                    happiness=75,
                    career_progress=70,
                ),
                milestones=["AWS Certified", "German B1", "Relocate to Berlin"],
            ),
        ],
    )


@router.post("/{simulation_id}/stress-test", summary="Black Swan stres testi")
async def stress_test(simulation_id: str, node_id: str):
    """
    Seçili dal için kriz senaryosu çalıştırır (ekonomik kriz, sağlık sorunu vb.)
    TODO: LangGraph BlackSwanAgent – Hafta 2
    """
    raise HTTPException(status_code=501, detail="Hafta 2'de implement edilecek.")
