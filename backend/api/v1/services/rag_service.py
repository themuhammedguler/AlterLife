"""
RAG Service – Topluluk Başarı Yolları Arama Servisi
In-memory keyword + cosine similarity tabanlı arama.
Pinecone / Vertex AI Vector Search (opsiyonel) ile genişletilebilir.
"""

import math
import re
import json
import os
from typing import List, Dict, Optional

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
        "country_to": "Germany"
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
        "country_to": None
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
        "country_to": None
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
        "country_to": "Canada"
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
        "country_to": None
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
        "country_to": "USA"
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
        "country_to": "Netherlands"
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
        "country_to": None
    }
]


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
    
    # Tüm yol metinlerini hazırla
    path_texts = [_tokenize(_path_to_text(p)) for p in COMMUNITY_SEED_PATHS]
    
    # Vocab oluştur
    vocab_set: set = set(query_tokens)
    for tokens in path_texts:
        vocab_set.update(tokens)
    vocab = sorted(vocab_set)
    
    if not vocab:
        return COMMUNITY_SEED_PATHS[:top_k]
    
    # Query vektörü
    query_vec = _build_term_vector(query_tokens, vocab)
    
    # Her yol için similarity hesapla
    scored = []
    for i, path in enumerate(COMMUNITY_SEED_PATHS):
        path_vec = _build_term_vector(path_texts[i], vocab)
        score = _cosine_similarity(query_vec, path_vec)
        scored.append((score, path))
    
    # Sırala ve top_k döndür
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]


def get_all_paths(limit: int = 20) -> List[dict]:
    """Tüm topluluk yollarını döner."""
    return COMMUNITY_SEED_PATHS[:limit]


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
        "shared_by": "anonymous"
    }
    COMMUNITY_SEED_PATHS.append(new_path)
    return new_path
