"""
Skills Router – /api/v1/skills
Yetenek Ağacı: DB'den yükle, Gemini ile kaynak öner, XP ekle
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, get_skills, save_skills
from api.v1.services.resource_service import get_dynamic_resources

router = APIRouter(prefix="/skills")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SkillNode(BaseModel):
    skill_id: str
    name: str
    category: str
    level: int
    max_level: int = 5
    xp: int
    is_unlocked: bool
    prerequisites: List[str] = []
    description: Optional[str] = None


class SkillResource(BaseModel):
    title: str
    platform: str
    url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None


class SkillTreeResponse(BaseModel):
    nodes: List[SkillNode]


class AddXPRequest(BaseModel):
    xp_amount: int


class AddXPResponse(BaseModel):
    skill_id: str
    new_xp: int
    new_level: int
    level_up: bool
    message: str


# ── Catalog ───────────────────────────────────────────────────────────────────

FULL_SKILL_CATALOG = [
    {"skill_id": "python", "name": "Python", "category": "Backend", "max_level": 5, "prerequisites": [], "description": "Nesne yönelimli programlama ve Python ekosistemi."},
    {"skill_id": "javascript", "name": "JavaScript", "category": "Frontend", "max_level": 5, "prerequisites": [], "description": "ES6+, async/await ve modern JS patterns."},
    {"skill_id": "react", "name": "React / Next.js", "category": "Frontend", "max_level": 5, "prerequisites": ["javascript"], "description": "Bileşen tabanlı UI, hooks ve App Router."},
    {"skill_id": "fastapi", "name": "FastAPI", "category": "Backend", "max_level": 5, "prerequisites": ["python"], "description": "Yüksek performanslı REST API ve Pydantic."},
    {"skill_id": "docker", "name": "Docker", "category": "DevOps", "max_level": 5, "prerequisites": [], "description": "Container oluşturma ve çok katmanlı build."},
    {"skill_id": "kubernetes", "name": "Kubernetes", "category": "DevOps", "max_level": 5, "prerequisites": ["docker"], "description": "Container orkestrasyonu ve pod yönetimi."},
    {"skill_id": "aws_fundamentals", "name": "AWS Fundamentals", "category": "Cloud", "max_level": 5, "prerequisites": [], "description": "IAM, EC2, S3, RDS ve temel AWS hizmetleri."},
    {"skill_id": "aws_vpc", "name": "AWS VPC & Networking", "category": "Cloud", "max_level": 5, "prerequisites": ["aws_fundamentals"], "description": "VPC, subnet, security group ve NAT gateway."},
    {"skill_id": "german_a1", "name": "Almanca A1", "category": "Dil", "max_level": 5, "prerequisites": [], "description": "Temel Almanca: selamlama ve gündelik ifadeler."},
    {"skill_id": "german_b1", "name": "Almanca B1", "category": "Dil", "max_level": 5, "prerequisites": ["german_a1"], "description": "İş hayatı ve Almanya vize süreçleri için B1."},
    {"skill_id": "system_design", "name": "System Design", "category": "Backend", "max_level": 5, "prerequisites": ["docker"], "description": "Ölçeklenebilir mimari ve cache stratejileri."},
    {"skill_id": "english_professional", "name": "Profesyonel İngilizce", "category": "Soft", "max_level": 5, "prerequisites": [], "description": "İş yazışmaları ve mülakat becerileri."},
]

SKILL_RESOURCES_MOCK = {
    "python": [
        {"title": "Python Full Course for Beginners", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "duration": "4h 26m", "level": "Beginner"},
        {"title": "100 Days of Code: Python Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/100-days-of-code/", "duration": "60h", "level": "Beginner"},
        {"title": "Python Official Tutorial", "platform": "Docs", "url": "https://docs.python.org/3/tutorial/", "level": "All"},
    ],
    "javascript": [
        {"title": "JavaScript Crash Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "duration": "1h 40m", "level": "Beginner"},
        {"title": "The Complete JavaScript Course 2024", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "duration": "69h", "level": "Beginner"},
        {"title": "MDN JavaScript", "platform": "Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "level": "All"},
    ],
    "react": [
        {"title": "React Full Tutorial with Projects", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "duration": "12h", "level": "Beginner"},
        {"title": "Next.js 14 Full Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=wm5gMKuwSYk", "duration": "3h", "level": "Intermediate"},
        {"title": "React Official Docs", "platform": "Docs", "url": "https://react.dev/learn", "level": "All"},
    ],
    "fastapi": [
        {"title": "FastAPI Full Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=7t2alSnE2-I", "duration": "9h", "level": "Beginner"},
        {"title": "FastAPI Official Tutorial", "platform": "Docs", "url": "https://fastapi.tiangolo.com/tutorial/", "level": "All"},
    ],
    "docker": [
        {"title": "Docker Tutorial for Beginners", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "duration": "2h 10m", "level": "Beginner"},
        {"title": "Docker & Kubernetes: The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/", "duration": "21h", "level": "Intermediate"},
        {"title": "Docker Official Docs", "platform": "Docs", "url": "https://docs.docker.com/get-started/", "level": "All"},
    ],
    "kubernetes": [
        {"title": "Kubernetes Tutorial for Beginners", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "duration": "4h", "level": "Beginner"},
        {"title": "Kubernetes Official Docs", "platform": "Docs", "url": "https://kubernetes.io/docs/tutorials/", "level": "All"},
    ],
    "aws_fundamentals": [
        {"title": "AWS Cloud Practitioner Full Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc", "duration": "13h", "level": "Beginner"},
        {"title": "AWS Getting Started", "platform": "Docs", "url": "https://aws.amazon.com/getting-started/", "level": "Beginner"},
    ],
    "aws_vpc": [
        {"title": "AWS VPC Explained in 5 Minutes", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=2doSoMN2xvI", "duration": "5m", "level": "Beginner"},
        {"title": "What Is Amazon VPC", "platform": "Docs", "url": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html", "level": "All"},
    ],
    "german_a1": [
        {"title": "German for Beginners A1 Complete", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=hnHCBFwh6b4", "duration": "5h", "level": "Beginner"},
        {"title": "Duolingo Almanca", "platform": "Article", "url": "https://www.duolingo.com/course/de/en/Learn-German", "level": "Beginner"},
    ],
    "german_b1": [
        {"title": "Goethe Institut B1 Prüfung", "platform": "Docs", "url": "https://www.goethe.de/en/spr/kup/prf/prf/gb1.html", "level": "Intermediate"},
        {"title": "Deutsche Welle B1", "platform": "Article", "url": "https://www.dw.com/en/learn-german/b1/s-2526", "level": "Intermediate"},
    ],
    "system_design": [
        {"title": "System Design for Beginners", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=i53Gi_K3o7I", "duration": "2h", "level": "Advanced"},
        {"title": "Grokking System Design", "platform": "Article", "url": "https://www.designgurus.io/course/grokking-the-system-design-interview", "level": "Intermediate"},
    ],
    "english_professional": [
        {"title": "Business English for Professionals", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=a_V-9T9Pkls", "duration": "1h", "level": "Intermediate"},
        {"title": "Coursera Business English", "platform": "Article", "url": "https://www.coursera.org/specializations/business-english", "level": "Intermediate"},
    ],
}


def _build_default_skill_tree(field: str = "") -> List[dict]:
    field_lower = (field or "").lower()
    is_tech = any(k in field_lower for k in ["yazılım", "developer", "engineer", "software", "tech", "it", "cloud"])
    is_abroad = any(k in field_lower for k in ["almanya", "germany", "avrupa", "abroad", "yurt dışı"])
    nodes = []
    for item in FULL_SKILL_CATALOG:
        sid = item["skill_id"]
        level, xp, unlocked = 0, 0, not item["prerequisites"]
        if is_tech and sid in ("python", "javascript", "docker", "aws_fundamentals"):
            level, xp, unlocked = 2, 400, True
        if is_abroad and sid == "german_a1":
            level, xp, unlocked = 1, 200, True
        if sid == "english_professional":
            level, xp, unlocked = 2, 400, True
        nodes.append({**item, "level": level, "xp": xp, "is_unlocked": unlocked})
    return nodes


def _get_resources(skill_id: str, skill_name: str) -> List[dict]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai, json
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f'Suggest 3 high-quality learning resources for: "{skill_name}". Return JSON array with fields: title, platform, url, duration, level. No markdown.'
            raw = model.generate_content(prompt).text.strip().strip("```json").strip("```").strip()
            return json.loads(raw)[:5]
        except Exception as e:
            print(f"[Skills] Gemini failed: {e}")
    return SKILL_RESOURCES_MOCK.get(skill_id, [{"title": f"{skill_name} Tutorial", "platform": "Docs", "url": f"https://www.google.com/search?q={skill_name}+tutorial", "level": "Beginner"}])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/tree", response_model=SkillTreeResponse, summary="Kişiselleştirilmiş yetenek ağacı")
async def get_skill_tree(user_id: str = Depends(get_current_user_id)):
    existing = get_skills(user_id)
    if existing:
        return SkillTreeResponse(nodes=[SkillNode(**n) for n in existing])
    user = get_user(user_id) or {}
    field = user.get("field", "") or user.get("freeGoal", "")
    nodes = _build_default_skill_tree(field)
    save_skills(user_id, nodes)
    return SkillTreeResponse(nodes=[SkillNode(**n) for n in nodes])


@router.get("/{skill_id}/resources", response_model=List[SkillResource], summary="Yetenek kaynakları")
async def get_skill_resources(skill_id: str, user_id: str = Depends(get_current_user_id)):
    existing = get_skills(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Önce /skills/tree çağırın.")
    skill = next((n for n in existing if n["skill_id"] == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail=f"'{skill_id}' bulunamadı.")
    resources = await get_dynamic_resources(skill["name"])
    return [SkillResource(**r) for r in resources]


@router.post("/{skill_id}/xp", response_model=AddXPResponse, summary="Yeteneğe XP ekle")
async def add_skill_xp(skill_id: str, payload: AddXPRequest, user_id: str = Depends(get_current_user_id)):
    existing = get_skills(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Yetenek ağacı bulunamadı.")
    skill = next((n for n in existing if n["skill_id"] == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail=f"'{skill_id}' bulunamadı.")
    if not skill.get("is_unlocked"):
        raise HTTPException(status_code=400, detail="Bu yetenek henüz kilitli.")
    old_level = skill["level"]
    skill["xp"] = skill.get("xp", 0) + payload.xp_amount
    skill["level"] = min(skill["xp"] // 500, skill["max_level"])
    if skill["level"] >= 1:
        for node in existing:
            if skill_id in node.get("prerequisites", []) and not node["is_unlocked"]:
                if all(any(n["skill_id"] == p and n.get("level", 0) >= 1 for n in existing) for p in node["prerequisites"]):
                    node["is_unlocked"] = True
    save_skills(user_id, existing)
    level_up = skill["level"] > old_level
    return AddXPResponse(skill_id=skill_id, new_xp=skill["xp"], new_level=skill["level"], level_up=level_up,
                         message=f"{'⬆️ Seviye atladın!' if level_up else '✅ XP eklendi.'} {skill['name']} → Seviye {skill['level']}")


# ── Custom Skill Node CRUD ────────────────────────────────────────────────────

class CustomSkillRequest(BaseModel):
    name: str
    category: str = "Custom"
    description: Optional[str] = None
    prerequisites: List[str] = []
    max_level: int = 5
    canvas_x: Optional[float] = None
    canvas_y: Optional[float] = None


class NodePositionRequest(BaseModel):
    canvas_x: float
    canvas_y: float


@router.post("/custom", summary="🛠️ Özel yetenek düğümü ekle")
async def add_custom_skill(
    payload: CustomSkillRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının kendi yetenek ağacına özel bir düğüm eklemesini sağlar.
    """
    import time
    existing = get_skills(user_id) or []

    # Unique ID oluştur
    custom_id = f"custom_{int(time.time())}_{payload.name.lower().replace(' ', '_')[:12]}"

    # Önkoşulların var olduğunu doğrula
    existing_ids = {n["skill_id"] for n in existing}
    valid_prereqs = [p for p in payload.prerequisites if p in existing_ids]

    new_node = {
        "skill_id": custom_id,
        "name": payload.name,
        "category": payload.category,
        "description": payload.description or f"{payload.name} alanında uzmanlaşma yeteneği.",
        "level": 0,
        "max_level": payload.max_level,
        "xp": 0,
        "is_unlocked": len(valid_prereqs) == 0,  # Önkoşul yoksa açık başlat
        "prerequisites": valid_prereqs,
        "is_custom": True,
        "canvas_x": payload.canvas_x,
        "canvas_y": payload.canvas_y,
    }

    existing.append(new_node)
    save_skills(user_id, existing)

    return {
        "status": "success",
        "message": f"'{payload.name}' yeteneği ağacına eklendi.",
        "skill_id": custom_id,
        "node": new_node
    }


@router.patch("/{skill_id}/position", summary="📌 Düğüm canvas pozisyonunu kaydet")
async def update_skill_position(
    skill_id: str,
    payload: NodePositionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Sürükle-bırak editoründe düğümün canvas koordinatını günceller.
    """
    existing = get_skills(user_id) or []
    skill = next((n for n in existing if n["skill_id"] == skill_id), None)

    if not skill:
        raise HTTPException(status_code=404, detail=f"'{skill_id}' bulunamadı.")

    skill["canvas_x"] = payload.canvas_x
    skill["canvas_y"] = payload.canvas_y
    save_skills(user_id, existing)

    return {"status": "success", "skill_id": skill_id, "canvas_x": payload.canvas_x, "canvas_y": payload.canvas_y}


@router.delete("/{skill_id}/custom", summary="🗑️ Özel yetenek düğümünü sil")
async def delete_custom_skill(
    skill_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Yalnızca kullanıcının eklediği özel (is_custom=True) düğümleri siler.
    Sistem tarafından oluşturulan düğümleri silmeye izin vermez.
    """
    existing = get_skills(user_id) or []
    skill = next((n for n in existing if n["skill_id"] == skill_id), None)

    if not skill:
        raise HTTPException(status_code=404, detail=f"'{skill_id}' bulunamadı.")

    if not skill.get("is_custom"):
        raise HTTPException(status_code=403, detail="Yalnızca kendi oluşturduğunuz düğümleri silebilirsiniz.")

    updated = [n for n in existing if n["skill_id"] != skill_id]
    save_skills(user_id, updated)

    return {"status": "success", "message": f"'{skill['name']}' yeteneği ağaçtan kaldırıldı."}

