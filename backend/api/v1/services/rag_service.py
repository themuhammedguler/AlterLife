"""
RAG Service – Topluluk Başarı Yolları Arama Servisi
In-memory keyword + cosine similarity tabanlı arama.
Pinecone / Vertex AI Vector Search (opsiyonel) ile genişletilebilir.
"""

import hashlib
import math
import re
from typing import List, Dict, Optional

from api.v1.database import (
    get_community_memberships,
    get_community_paths,
    save_community_memberships,
    save_community_paths,
)

# ── Örnek Topluluk Yolları (Seed Data) ───────────────────────────────────────
# Gerçek uygulamada Firestore'dan çekilir
COMMUNITY_SEED_PATHS = [
    {
        "id": "path_001",
        "goal": "Almanya'da yazılım mühendisi olmak",
        "role": "Software Developer",
        "duration_months": 18,
        "steps": ["Python öğrendi", "AWS Solutions Architect sertifikası aldı", "B1 Almanca", "Berlin'de iş buldu"],
        "outcome": "Senior Backend Developer @ Berlin startupında €70k/yıl",
        "tags": ["almanya", "backend", "python", "aws", "göç"],
        "success": True,
        "country_from": "Turkey",
        "country_to": "Germany",
        "members_count": 42,
        "avg_progress": 68,
        "common_until_step": 2,
        "branches": [
            {"name": "Almanya'da çalışmak", "members_count": 24, "avg_progress": 71},
            {"name": "Almanya'da master", "members_count": 18, "avg_progress": 61},
        ],
    },
    {
        "id": "path_002",
        "goal": "Freelance kariyer ve finansal özgürlük",
        "role": "UI/UX Designer",
        "duration_months": 12,
        "steps": ["Figma ustalaştı", "Upwork profili açtı", "İlk 3 müşteri", "Aylık 3000$ gelir"],
        "outcome": "Full-time freelancer, 5000$/ay, tam lokasyon bağımsız",
        "tags": ["freelance", "tasarım", "figma", "remote", "finansal özgürlük"],
        "success": True,
        "country_from": "Turkey",
        "country_to": None,
        "members_count": 27,
        "avg_progress": 54,
        "common_until_step": 1,
        "branches": [
            {"name": "Upwork ağırlıklı", "members_count": 15, "avg_progress": 58},
            {"name": "Ajans müşterisi", "members_count": 12, "avg_progress": 49},
        ],
    },
    {
        "id": "path_003",
        "goal": "Startup kurmak ve seed funding almak",
        "role": "Startup Founder",
        "duration_months": 24,
        "steps": ["Fikir doğrulandı", "MVP geliştirildi", "Accelerator programına kabul", "Seed round €200k"],
        "outcome": "B2B SaaS startup, 3 çalışan, €200k seed",
        "tags": ["startup", "girişim", "mvp", "funding", "saas"],
        "success": True,
        "country_from": "Turkey",
        "country_to": None,
        "members_count": 19,
        "avg_progress": 46,
        "common_until_step": 1,
        "branches": [
            {"name": "B2B SaaS", "members_count": 11, "avg_progress": 52},
            {"name": "Consumer app", "members_count": 8, "avg_progress": 38},
        ],
    },
    {
        "id": "path_004",
        "goal": "Kanada'ya göç etmek",
        "role": "Software Developer",
        "duration_months": 30,
        "steps": ["IELTS 7.5 aldı", "Express Entry başvurusu", "İş teklifi Kanada'dan", "PR aldı"],
        "outcome": "Kanada'da permanent resident, $95k CAD/yıl",
        "tags": ["kanada", "göç", "express entry", "pr", "yazılım"],
        "success": True,
        "country_from": "Turkey",
        "country_to": "Canada",
        "members_count": 31,
        "avg_progress": 57,
        "common_until_step": 1,
        "branches": [
            {"name": "Express Entry", "members_count": 21, "avg_progress": 62},
            {"name": "Job offer", "members_count": 10, "avg_progress": 48},
        ],
    },
    {
        "id": "path_005",
        "goal": "Cloud ve DevOps kariyerine geçiş",
        "role": "Software Developer",
        "duration_months": 8,
        "steps": ["AWS CCP aldı", "Docker ve Kubernetes öğrendi", "Terraform sertifikası", "Yeni pozisyon"],
        "outcome": "DevOps Engineer, %40 maaş artışı",
        "tags": ["aws", "devops", "kubernetes", "terraform", "cloud", "geçiş"],
        "success": True,
        "country_from": "Turkey",
        "country_to": None,
        "members_count": 36,
        "avg_progress": 63,
        "common_until_step": 1,
        "branches": [
            {"name": "AWS/Cloud", "members_count": 22, "avg_progress": 67},
            {"name": "Kubernetes/SRE", "members_count": 14, "avg_progress": 56},
        ],
    },
    {
        "id": "path_006",
        "goal": "Yüksek lisans yapıp akademik kariyer",
        "role": "Student",
        "duration_months": 36,
        "steps": ["GRE 320 aldı", "ABD üniversitesine başvurdu", "Burs kazandı", "Araştırma yayını"],
        "outcome": "PhD öğrencisi, tam burslu, üniversite yurt dışında",
        "tags": ["yüksek lisans", "phd", "abd", "burs", "akademi"],
        "success": True,
        "country_from": "Turkey",
        "country_to": "USA",
        "members_count": 23,
        "avg_progress": 49,
        "common_until_step": 1,
        "branches": [
            {"name": "Tam burs", "members_count": 14, "avg_progress": 52},
            {"name": "Araştırma asistanlığı", "members_count": 9, "avg_progress": 43},
        ],
    },
    {
        "id": "path_007",
        "goal": "Hollanda'da data scientist olmak",
        "role": "Data Scientist",
        "duration_months": 15,
        "steps": ["Python ML sertifikası", "Kaggle competitions", "Hollanda CVsine uyarladı", "Amsterdam iş teklifi"],
        "outcome": "Data Scientist @ Amsterdam, €65k/yıl",
        "tags": ["hollanda", "data science", "machine learning", "amsterdam", "göç"],
        "success": True,
        "country_from": "Turkey",
        "country_to": "Netherlands",
        "members_count": 16,
        "avg_progress": 59,
        "common_until_step": 2,
        "branches": [
            {"name": "Data scientist", "members_count": 10, "avg_progress": 64},
            {"name": "ML engineer", "members_count": 6, "avg_progress": 51},
        ],
    },
    {
        "id": "path_008",
        "goal": "İngilizce içerik üretimi ve YouTube geliri",
        "role": "Content Creator",
        "duration_months": 20,
        "steps": ["Niche seçildi", "100 video çekildi", "5k abone", "Sponsorluk anlaşmaları"],
        "outcome": "Aylık 2000$ pasif gelir, topluluk 15k",
        "tags": ["youtube", "içerik", "pasif gelir", "ingilizce", "yaratıcı"],
        "success": True,
        "country_from": "Turkey",
        "country_to": None,
        "members_count": 21,
        "avg_progress": 44,
        "common_until_step": 1,
        "branches": [
            {"name": "YouTube", "members_count": 13, "avg_progress": 48},
            {"name": "Newsletter", "members_count": 8, "avg_progress": 37},
        ],
    }
]

COMMUNITY_MEMBERSHIPS: Dict[str, List[dict]] = {}


def _paths_store() -> List[dict]:
    stored = get_community_paths()
    if stored:
        return stored
    save_community_paths(COMMUNITY_SEED_PATHS)
    return COMMUNITY_SEED_PATHS


def _save_paths_store(paths: List[dict]) -> None:
    save_community_paths(paths)


# ── Tokenizer & TF-IDF Benzeri Arama ─────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    """Metni küçük harfe çevirip kelimelere böler."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]


def _build_term_vector(tokens: List[str], vocab: List[str]) -> List[float]:
    """Verilen vocab'a göre term frekansı vektörü oluşturur."""
    freq: Dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return [freq.get(v, 0) for v in vocab]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """İki vektör arasındaki cosine similarity hesaplar."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _path_to_text(path: dict) -> str:
    """Bir yolu aranabilir tam metne dönüştürür."""
    parts = [
        path.get("goal", ""),
        path.get("role", ""),
        path.get("outcome", ""),
        " ".join(path.get("steps", [])),
        " ".join(path.get("tags", [])),
        path.get("country_to", "") or "",
    ]
    return " ".join(parts)


def search_similar_paths(goal: str, top_k: int = 4) -> List[dict]:
    """
    Kullanıcının hedefine göre en benzer topluluk yollarını döner.
    Cosine similarity tabanlı in-memory arama.
    """
    query_tokens = _tokenize(goal)
    paths = _paths_store()
    
    # Tüm yol metinlerini hazırla
    path_texts = [_tokenize(_path_to_text(p)) for p in paths]
    
    # Vocab oluştur
    vocab_set: set = set(query_tokens)
    for tokens in path_texts:
        vocab_set.update(tokens)
    vocab = sorted(vocab_set)
    
    if not vocab:
        return paths[:top_k]
    
    # Query vektörü
    query_vec = _build_term_vector(query_tokens, vocab)
    
    # Her yol için similarity hesapla
    scored = []
    for i, path in enumerate(paths):
        path_vec = _build_term_vector(path_texts[i], vocab)
        score = _cosine_similarity(query_vec, path_vec)
        scored.append((score, path))
    
    # Sırala ve top_k döndür
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]


def get_all_paths(limit: int = 20) -> List[dict]:
    """Tüm topluluk yollarını döner."""
    return _paths_store()[:limit]


def anonymize_path(path: dict) -> dict:
    """Kişisel bilgileri maskeler (şimdilik anonim zaten)."""
    safe = {k: v for k, v in path.items() if k not in ("user_id", "email")}
    return safe


def add_community_path(user_id: str, goal: str, steps: List[str], outcome: str, tags: List[str]) -> dict:
    """
    Kullanıcının kendi başarı yolunu anonim olarak ekler.
    Gerçek uygulamada Firestore'a yazar.
    """
    import time
    new_path = {
        "id": f"path_{int(time.time())}",
        "goal": goal,
        "role": "Community Member",
        "duration_months": len(steps) * 2,
        "steps": steps,
        "outcome": outcome,
        "tags": tags,
        "success": True,
        "country_from": "Unknown",
        "country_to": None,
        "shared_by": "anonymous",
        "members_count": 1,
        "avg_progress": 100,
        "common_until_step": max(0, min(1, len(steps) - 1)),
        "branches": [
            {"name": "Ana rota", "members_count": 1, "avg_progress": 100},
        ],
    }
    paths = _paths_store()
    paths.append(new_path)
    _save_paths_store(paths)
    return new_path


def get_path_by_id(path_id: str) -> Optional[dict]:
    return next((path for path in _paths_store() if path.get("id") == path_id), None)


def join_path(user_id: str, path_id: str, branch: Optional[str] = None) -> dict:
    paths = _paths_store()
    path = next((item for item in paths if item.get("id") == path_id), None)
    if not path:
        raise ValueError("Path not found")

    branch_name = branch or (path.get("branches") or [{"name": "Ana rota"}])[0]["name"]
    progress = _deterministic_progress(user_id, path_id, len(path.get("steps", [])))
    membership = {
        "path_id": path_id,
        "goal": path["goal"],
        "branch": branch_name,
        "completed_steps": progress["completed_steps"],
        "total_steps": progress["total_steps"],
        "progress_percent": progress["progress_percent"],
        "current_step": progress["current_step"],
        "peer_rank": progress["peer_rank"],
        "joined_as": "anonymous",
    }
    memberships = get_community_memberships(user_id) or COMMUNITY_MEMBERSHIPS.setdefault(user_id, [])
    existing = next((item for item in memberships if item["path_id"] == path_id), None)
    if existing:
        existing.update(membership)
    else:
        memberships.append(membership)
        path["members_count"] = path.get("members_count", 0) + 1
        _save_paths_store(paths)
    save_community_memberships(user_id, memberships)
    return membership


def get_user_memberships(user_id: str) -> List[dict]:
    return get_community_memberships(user_id) or COMMUNITY_MEMBERSHIPS.get(user_id, [])


def get_cohort_for_path(path_id: str) -> dict:
    path = get_path_by_id(path_id)
    if not path:
        raise ValueError("Path not found")

    members = _sample_members(path)
    completed = [member for member in members if member["progress_percent"] >= 100]
    stuck = [member for member in members if member["status"] == "stuck"]
    return {
        "path_id": path_id,
        "goal": path["goal"],
        "members_count": path.get("members_count", len(members)),
        "avg_progress": path.get("avg_progress", 0),
        "completion_rate": round(len(completed) / max(len(members), 1) * 100),
        "stuck_count": len(stuck),
        "common_until": path.get("steps", [])[: path.get("common_until_step", 1) + 1],
        "branches": path.get("branches", []),
        "members": members,
    }


def build_community_overview(limit: int = 20) -> dict:
    paths = get_all_paths(limit)
    cohorts = [get_cohort_for_path(path["id"]) for path in paths]
    total_members = sum(cohort["members_count"] for cohort in cohorts)
    avg_progress = round(sum(cohort["avg_progress"] for cohort in cohorts) / max(len(cohorts), 1))
    hot_paths = sorted(cohorts, key=lambda cohort: cohort["members_count"], reverse=True)[:3]
    needs_help = sorted(cohorts, key=lambda cohort: cohort["stuck_count"], reverse=True)[:3]
    return {
        "total_cohorts": len(cohorts),
        "total_members": total_members,
        "avg_progress": avg_progress,
        "hot_paths": hot_paths,
        "needs_help": needs_help,
    }


def _deterministic_progress(user_id: str, path_id: str, total_steps: int) -> dict:
    total = max(total_steps, 1)
    seed = int(hashlib.sha1(f"{user_id}:{path_id}".encode("utf-8")).hexdigest()[:8], 16)
    completed = min(total, seed % (total + 1))
    current_idx = min(completed, total - 1)
    return {
        "completed_steps": completed,
        "total_steps": total,
        "progress_percent": round(completed / total * 100),
        "current_step": current_idx + 1,
        "peer_rank": (seed % 18) + 1,
    }


def _sample_members(path: dict) -> List[dict]:
    aliases = ["A-17", "B-04", "C-92", "D-31", "E-66", "F-28"]
    statuses = ["on_track", "on_track", "stuck", "ahead", "on_track", "stuck"]
    total = max(len(path.get("steps", [])), 1)
    members = []
    for idx, alias in enumerate(aliases):
        completed = min(total, max(0, idx % (total + 1)))
        members.append({
            "alias": alias,
            "branch": (path.get("branches") or [{"name": "Ana rota"}])[idx % len(path.get("branches") or [1])]["name"],
            "completed_steps": completed,
            "total_steps": total,
            "progress_percent": round(completed / total * 100),
            "current_step": min(completed + 1, total),
            "status": statuses[idx],
        })
    return members
