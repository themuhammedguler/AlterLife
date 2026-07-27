"""
Simulations Router – /api/v1/simulations
Dallanan Karar Ağacı ve "What If" Engine
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import hashlib
from typing import Optional, List, Any, Literal

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_simulation_tree, get_user
from api.v1.services.simulation_service import (
    generate_initial_tree_data,
    add_branch_node,
    inject_crisis
)
from api.v1.services.research_service import search_live_resources

router = APIRouter(prefix="/simulations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SimulationGenerateRequest(BaseModel):
    target: str = Field(min_length=3, max_length=500)
    current_profile: Optional[dict] = None   # Kullanıcının mevcut profil verisi


class BranchRequest(BaseModel):
    parent_node_id: str = Field(min_length=1, max_length=120)
    decision_text: str = Field(min_length=3, max_length=500)


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
    milestones: List[str] = Field(default_factory=list)


class SimulationTreeResponse(BaseModel):
    simulation_id: str
    user_id: str
    initial_target: str
    nodes: List[SimulationNode]


class ActionPlanRequest(BaseModel):
    friend_code: Optional[str] = Field(default=None, min_length=6, max_length=32)


class ActionPlanStep(BaseModel):
    title: str
    description: str
    duration: str
    proof: str


class ActionPlanResource(BaseModel):
    title: str
    platform: str
    url: str
    reason: str


class SharedPath(BaseModel):
    code: str
    common_until: str
    together: List[str]
    divergence_options: List[str]


class ActionPlanResponse(BaseModel):
    simulation_id: str
    node_id: str
    selected_goal: str
    summary: str
    realism_score: int
    fun_angle: str
    steps: List[ActionPlanStep]
    resources: List[ActionPlanResource]
    done_so_far: List[str]
    shared_path: SharedPath
    research_note: str


def _require_simulation_owner(simulation_id: str, user_id: str) -> None:
    if simulation_id != f"sim_{user_id}":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu simülasyona erişim yetkiniz yok.",
        )


def _find_node_or_404(tree: dict, node_id: str) -> dict:
    node = next((n for n in tree.get("nodes", []) if n["node_id"] == node_id), None)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"'{node_id}' bulunamadı.")
    return node


def _path_to_node(tree: dict, node_id: str) -> List[dict]:
    nodes = tree.get("nodes", [])
    by_id = {node["node_id"]: node for node in nodes}
    path = []
    current = by_id.get(node_id)
    while current:
        path.insert(0, current)
        parent_id = current.get("parent")
        current = by_id.get(parent_id) if parent_id else None
    return path


def _goal_keywords(goal: str) -> set[str]:
    lowered = goal.lower()
    tokens = {part.strip(".,;:!?()[]{}\"'").lower() for part in lowered.split()}
    aliases = set()
    if any(word in lowered for word in ("almanya", "germany", "berlin")):
        aliases.update({"almanya", "germany", "berlin", "visa", "vize", "german", "almanca"})
    if any(word in lowered for word in ("cloud", "aws", "devops", "kubernetes")):
        aliases.update({"cloud", "aws", "devops", "kubernetes", "docker"})
    if any(word in lowered for word in ("master", "yüksek", "lisans", "university")):
        aliases.update({"master", "university", "daad", "study", "üniversite"})
    if any(word in lowered for word in ("work", "çalış", "iş", "career", "kariyer")):
        aliases.update({"work", "job", "career", "linkedin", "cv", "çalışma"})
    return tokens | aliases


def _resource_pack(goal: str, mode: Literal["work", "study", "balanced"]) -> List[ActionPlanResource]:
    keywords = _goal_keywords(goal)
    resources = [
        {
            "title": "Make it in Germany - Working in Germany",
            "platform": "Official",
            "url": "https://www.make-it-in-germany.com/en/working-in-germany",
            "reason": "Almanya'da çalışma, vize ve meslek denkliği tarafını resmi kaynaktan kontrol etmek için.",
            "tags": {"almanya", "germany", "work", "visa", "vize", "çalışma"},
        },
        {
            "title": "DAAD - International Study Programmes",
            "platform": "Official",
            "url": "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/",
            "reason": "Almanya'da yüksek lisans isteyen arkadaşınla ortak aşamadan sonra akademik kola ayrılmak için.",
            "tags": {"almanya", "germany", "master", "study", "daad", "university", "üniversite"},
        },
        {
            "title": "Anabin - Recognition and University Database",
            "platform": "Official",
            "url": "https://anabin.kmk.org/anabin.html",
            "reason": "Diploma/üniversite tanınırlığını erken kontrol etmek gerçekçilik skorunu yükseltir.",
            "tags": {"almanya", "germany", "master", "work", "recognition", "denklik"},
        },
        {
            "title": "Europass CV Builder",
            "platform": "Tool",
            "url": "https://europass.europa.eu/en/create-europass-cv",
            "reason": "Avrupa formatında CV hazırlayıp iş veya okul başvurularında ortak temel üretmek için.",
            "tags": {"work", "job", "career", "cv", "master", "study"},
        },
        {
            "title": "AWS Skill Builder - Cloud Practitioner",
            "platform": "Course",
            "url": "https://skillbuilder.aws/learn",
            "reason": "Cloud/DevOps iş kolu için doğrulanabilir teknik temel ve sertifika rotası sağlar.",
            "tags": {"cloud", "aws", "devops", "work", "career"},
        },
        {
            "title": "Kubernetes Documentation - Tutorials",
            "platform": "Docs",
            "url": "https://kubernetes.io/docs/tutorials/",
            "reason": "Cloud Engineer yolu için proje ve portfolyo üretmeye uygun resmi teknik kaynak.",
            "tags": {"cloud", "kubernetes", "devops", "docker", "work"},
        },
        {
            "title": "Goethe-Institut - German Exams",
            "platform": "Official",
            "url": "https://www.goethe.de/en/spr/kup/prf.html",
            "reason": "Almanca seviyesini ölçülebilir hale getirip vize, okul ve iş başvurularını güçlendirmek için.",
            "tags": {"almanya", "german", "almanca", "study", "work"},
        },
        {
            "title": "LinkedIn Jobs - Germany",
            "platform": "Search",
            "url": "https://www.linkedin.com/jobs/search/?location=Germany",
            "reason": "Gerçek ilanlardan maaş, beceri ve şehir beklentisini okumak için.",
            "tags": {"germany", "work", "job", "career", "linkedin"},
        },
    ]
    if mode == "study":
        priority = {"daad", "study", "master", "university", "almanca"}
    elif mode == "work":
        priority = {"work", "job", "career", "cloud", "aws", "linkedin"}
    else:
        priority = {"almanya", "germany", "cv", "almanca"}

    scored = []
    for item in resources:
        score = len((keywords | priority) & item["tags"])
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    selected = [ActionPlanResource(**{k: v for k, v in item.items() if k != "tags"}) for _, item in scored[:4]]
    live_results = search_live_resources(f"{goal} reliable official resources", 2)
    for result in live_results:
        if result.get("url") and all(existing.url != result["url"] for existing in selected):
            selected.append(ActionPlanResource(
                title=result.get("title", "Araştırma sonucu"),
                platform="Live Search" if result.get("source") != "fallback" else "Trusted",
                url=result["url"],
                reason=result.get("snippet") or "Hedef için güncel/ilgili araştırma sonucu.",
            ))
    return selected[:5]


def _infer_mode(goal: str) -> Literal["work", "study", "balanced"]:
    lowered = goal.lower()
    if any(word in lowered for word in ("master", "yüksek", "lisans", "üniversite", "study", "school")):
        return "study"
    if any(word in lowered for word in ("work", "çalış", "iş", "job", "career", "cloud", "engineer")):
        return "work"
    return "balanced"


def _build_action_plan(tree: dict, node: dict, user_id: str, friend_code: Optional[str]) -> ActionPlanResponse:
    selected_goal = node["decision_name"]
    full_goal = f"{tree.get('initial_target', '')} / {selected_goal}"
    mode = _infer_mode(full_goal)
    path = _path_to_node(tree, node["node_id"])
    done_so_far = [
        f"{idx}. {path_node['decision_name']}: {path_node.get('description', '')[:120]}"
        for idx, path_node in enumerate(path, start=1)
    ]
    common_goal = "Almanya hazırlığı" if "almanya" in full_goal.lower() or "germany" in full_goal.lower() else "ortak temel hazırlık"
    shared_seed = friend_code or f"{user_id}:{tree['simulation_id']}:{node['node_id']}"
    code = hashlib.sha1(shared_seed.encode("utf-8")).hexdigest()[:8].upper()
    common_until = "B1 Almanca + CV/portfolyo + bütçe planı"
    if mode == "study":
        divergence = [
            "Sen: üniversite/DAAD başvuruları, motivasyon mektubu, akademik referans",
            "Arkadaşın: iş ilanları, CV optimizasyonu, recruiter görüşmeleri",
        ]
    elif mode == "work":
        divergence = [
            "Sen: iş başvuruları, teknik portfolyo, vize/Blue Card hazırlığı",
            "Arkadaşın: master programları, DAAD filtreleri, akademik belge hazırlığı",
        ]
    else:
        divergence = [
            "Sen: hızlı iş/gelir odaklı rota",
            "Arkadaşın: eğitim ve şehir keşfi odaklı rota",
        ]

    steps = [
        ActionPlanStep(
            title="Hedefi görev kontratına çevir",
            description=f"'{selected_goal}' dalını 12 haftalık sprintlere böl; kararın ölçülebilir çıktısını yaz.",
            duration="1 gün",
            proof="Simülasyon dalında hedef seçildi ve başarı kriteri yazıldı.",
        ),
        ActionPlanStep(
            title="Ortak hazırlık hattını kur",
            description=f"Arkadaşınla {common_goal} için aynı kontrol listesini kullan: dil, bütçe, belge, CV ve şehir araştırması.",
            duration="2 hafta",
            proof="Ortak yol kodu paylaşıldı, aynı checklistte en az 5 madde tamamlandı.",
        ),
        ActionPlanStep(
            title="Kaynaklardan kanıt üret",
            description="Her kaynak için kısa not çıkar; öğrendiğin şeyi CV, portfolyo, başvuru dosyası veya karar ağacına bağla.",
            duration="3-6 hafta",
            proof="En az 2 kaynak tamamlandı ve kütüphanede işaretlendi.",
        ),
        ActionPlanStep(
            title="Ayrışma noktasını seç",
            description="Ortak hazırlık tamamlanınca biri çalışma, diğeri yüksek lisans gibi ayrı dala geçebilir; metrikleri tekrar karşılaştır.",
            duration="1 hafta",
            proof="Arkadaş koduyla ortak aşama görüldü ve yeni alt dal üretildi.",
        ),
        ActionPlanStep(
            title="Gerçek dünya testi yap",
            description="İlan, okul, vize veya bütçe verisini kontrol edip en gerçekçi seçeneği seç; eğlenceli kısmı RPG quest olarak takip et.",
            duration="Sürekli",
            proof="Black Swan testi çalıştırıldı ve risk azaltma görevi eklendi.",
        ),
    ]

    stress = node.get("metrics", {}).get("stress_level", 50)
    career = node.get("metrics", {}).get("career_progress", 40)
    happiness = node.get("metrics", {}).get("happiness", 60)
    realism = max(35, min(95, int((career * 0.45) + (happiness * 0.25) + ((100 - stress) * 0.3))))
    if "almanya" in full_goal.lower() or "germany" in full_goal.lower():
        fun_angle = "Co-op Germany run: aynı ana görevler, sonra biri Work Quest'e biri Master Quest'e ayrılıyor."
    else:
        fun_angle = "Co-op life route: ortak hazırlık boss'unu geç, sonra karakter sınıfına göre dallan."

    return ActionPlanResponse(
        simulation_id=tree["simulation_id"],
        node_id=node["node_id"],
        selected_goal=selected_goal,
        summary=f"Bu dal hedef seçilirse ana strateji: {selected_goal}. Önce ortak hazırlığı bitir, sonra çalışma/eğitim gibi ayrışan yolu netleştir.",
        realism_score=realism,
        fun_angle=fun_angle,
        steps=steps,
        resources=_resource_pack(full_goal, mode),
        done_so_far=done_so_far,
        shared_path=SharedPath(
            code=code,
            common_until=common_until,
            together=[
                "Dil seviyesi ve haftalık çalışma ritmi",
                "Bütçe, belge ve şehir karşılaştırması",
                "CV/portfolyo veya başvuru dosyasının ortak kalite kontrolü",
            ],
            divergence_options=divergence,
        ),
        research_note="Kaynaklar resmi ve yüksek güvenilirlikli sayfalardan seçilir; API anahtarları tanımlandığında canlı arama katmanı bu listeyi güncel sonuçlarla genişletebilir.",
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=SimulationTreeResponse, summary="Ana simülasyon dalını üret (LangGraph + Groq)")
async def generate_simulation(payload: SimulationGenerateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının hedefine göre LangGraph Orchestrator aracılığıyla
    Groq ile ana karar ağacı dalını oluşturur.
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simülasyon oluşturma başarısız."
        )


@router.post("/{simulation_id}/branch", response_model=SimulationNode, summary="'What If?' – Yeni dal üret")
async def create_branch(simulation_id: str, payload: BranchRequest, user_id: str = Depends(get_current_user_id)):
    """
    Mevcut bir karar düğümünden yeni bir 'What If' dalı türetir.
    Örn: "Aşık olursam ne olur?" → yeni node ve metrikler
    """
    _require_simulation_owner(simulation_id, user_id)
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dallanma oluşturma başarısız."
        )


@router.get("/{simulation_id}/tree", response_model=SimulationTreeResponse, summary="Karar ağacını getir")
async def get_tree(simulation_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının tüm karar ağacını JSON olarak döner (interaktif harita için).
    """
    _require_simulation_owner(simulation_id, user_id)
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


@router.post("/{simulation_id}/nodes/{node_id}/action-plan", response_model=ActionPlanResponse, summary="Seçili dalı hedefe çevir")
async def create_action_plan(
    simulation_id: str,
    node_id: str,
    payload: ActionPlanRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Seçili karar dalı için uygulanabilir yol haritası, kaynak önerileri,
    yapılanlar ve arkadaşla ortak/ayrışan rota kodu üretir.
    """
    _require_simulation_owner(simulation_id, user_id)
    tree = get_simulation_tree(simulation_id)
    if not tree:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simülasyon bulunamadı.")
    node = _find_node_or_404(tree, node_id)
    return _build_action_plan(tree, node, user_id, payload.friend_code)


@router.post("/{simulation_id}/stress-test", response_model=SimulationNode, summary="Black Swan stres testi")
async def stress_test(simulation_id: str, node_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Seçili dal için kriz senaryosu çalıştırır (ekonomik kriz, sağlık sorunu vb.)
    """
    _require_simulation_owner(simulation_id, user_id)
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stres testi başarısız."
        )
