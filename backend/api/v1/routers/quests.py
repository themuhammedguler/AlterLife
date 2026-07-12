"""
Quests Router – /api/v1/quests
Günlük Görevler ve XP Doğrulama
"""

import os
import json
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user, save_user, get_daily_quests, save_daily_quests, get_simulation_tree
from api.v1.services.sync_service import sync_and_verify_quests

router = APIRouter(prefix="/quests")


# ── Schemas ───────────────────────────────────────────────────────────────────

class DailyQuest(BaseModel):
    quest_id: str
    title: str
    description: str
    xp_reward: int
    status: str             # "pending" | "completed" | "failed"
    verified_by: str        # "manual" | "calendar_sync" | "github_commit"
    resource_link: Optional[str] = None
    completed_at: Optional[str] = None


class QuestVerifyResponse(BaseModel):
    quest_id: str
    status: str
    xp_earned: int
    new_total_xp: int
    level_up: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/daily", response_model=List[DailyQuest], summary="Günlük görevleri getir")
async def get_daily(user_id: str = Depends(get_current_user_id)):
    """
    Kullanıcının aktif karar dalına göre bugünün 3 mikro görevini döner.
    Görevleri veritabanına kaydeder, böylece gün boyunca durumları korunur.
    """
    # 1. Kaydedilmiş bugünkü görevleri veritabanından çekmeyi dene
    saved_quests = await sync_and_verify_quests(user_id)
    today_str = str(date.today())
    
    # Bugünün görevleri zaten oluşturulmuş mu kontrol et
    if saved_quests:
        # Eğer içlerinden biri bugün oluşturulduysa veya tamamlanmadıysa dön
        # Basitlik açısından, quest listesinde bugüne ait tarih kontrolü yapabiliriz
        # ya da eğer varsa direkt döneriz
        return [DailyQuest(**q) for q in saved_quests]

    # 2. Değilse, yeni görevler üret
    # Kullanıcının aktif milestone'unu bul
    active_milestone = "AWS bulut temellerini ve ağ bileşenlerini anlama."
    user_role = "Software Developer"
    
    user_data = get_user(user_id)
    if user_data:
        user_role = user_data.get("profile", {}).get("role", "Software Developer")
        
    sim_id = f"sim_{user_id}"
    tree = get_simulation_tree(sim_id)
    if tree and tree.get("nodes"):
        # Son eklenen düğümün hedeflerini incele
        last_node = tree["nodes"][-1]
        milestones = last_node.get("milestones", [])
        if milestones:
            active_milestone = milestones[0]
            
    # AI ile görev üretmeyi dene
    api_key = os.getenv("GOOGLE_API_KEY")
    quests = []
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
            
            prompt = f"""
            Kullanıcının rolü: {user_role}
            Kullanıcının aktif hedefi/milestone'u: "{active_milestone}"
            
            Bu hedefe yönelik bugün tamamlanması gereken 3 mikro görev üret.
            Görev türleri şunlar olsun:
            1. Teorik Öğrenim (20 dk döküman veya video okuma).
            2. Pratik Uygulama (Küçük bir kodlama veya uygulama adımı).
            3. Kişisel Gelişim/Dil/Sosyal (Duolingo çalışması, makale okuma, veya networking).
            
            Yanıt formatı tam olarak şu JSON listesi yapısında olmalıdır:
            [
              {{
                "quest_id": "qst_theory",
                "title": "Görev Başlığı",
                "description": "Detaylı açıklama...",
                "xp_reward": 150,
                "status": "pending",
                "verified_by": "calendar_sync",
                "resource_link": "https://aws.amazon.com/ veya ilgili bir resmi döküman linki"
              }},
              {{
                "quest_id": "qst_practice",
                "title": "Görev Başlığı",
                "description": "Detaylı açıklama...",
                "xp_reward": 200,
                "status": "pending",
                "verified_by": "github_commit",
                "resource_link": null
              }},
              {{
                "quest_id": "qst_general",
                "title": "Görev Başlığı",
                "description": "Detaylı açıklama...",
                "xp_reward": 50,
                "status": "pending",
                "verified_by": "manual",
                "resource_link": "https://www.duolingo.com"
              }}
            ]
            """
            response = model.generate_content(prompt)
            quests = json.loads(response.text)
        except Exception as e:
            print(f"[Quests] Gemini error generating quests: {e}. Falling back to default role-based quests.")
            quests = []

    # Fallback / Mock quests if AI fails or no key
    if not quests:
        if "design" in user_role.lower() or "tasarım" in user_role.lower() or "ui" in user_role.lower():
            quests = [
                {
                    "quest_id": "qst_theory",
                    "title": "Figma Auto-Layout İncelemesi",
                    "description": "Figma Auto-Layout v5 özelliklerini resmi dökümantasyondan oku ve örnek tasarımları incele (20 dk).",
                    "xp_reward": 150,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": "https://help.figma.com/hc/en-us/articles/360040451373-Create-dynamic-designs-with-Auto-layout"
                },
                {
                    "quest_id": "qst_practice",
                    "title": "Mobil Arayüz Kart Tasarımı",
                    "description": "Dribbble veya Behance esintili modern, glassmorphic bir ürün kartı tasarla ve prototipini hazırla.",
                    "xp_reward": 200,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": None
                },
                {
                    "quest_id": "qst_general",
                    "title": "Portfolyo Güncelleme Adımı",
                    "description": "Behance portfolyona son yaptığın projelerden bir taslak veya ekran görüntüsü ekle.",
                    "xp_reward": 50,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": "https://www.behance.net"
                }
            ]
        elif "startup" in user_role.lower() or "girişim" in user_role.lower():
            quests = [
                {
                    "quest_id": "qst_theory",
                    "title": "Müşteri Mülakatı Metodolojisi",
                    "description": "The Mom Test kitabından 'iyi soru sorma' kurallarını özetleyen makaleyi oku (15 dk).",
                    "xp_reward": 150,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": "https://www.lennysnewsletter.com/p/the-mom-test"
                },
                {
                    "quest_id": "qst_practice",
                    "title": "Landing Page MVP Taslağı",
                    "description": "Girişim fikrin için tek sayfalık bir landing page tasarımı çiz veya bir No-Code şablonu ayağa kaldır.",
                    "xp_reward": 200,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": None
                },
                {
                    "quest_id": "qst_general",
                    "title": "İngilizce Sunum Pratiği",
                    "description": "Asansör konuşmanı (pitch deck) ayna karşısında 3 dakika boyunca İngilizce olarak sun.",
                    "xp_reward": 50,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": "https://www.ycombinator.com/library/4D-how-to-pitch-your-startup"
                }
            ]
        else:
            # Software developer and default fallback
            quests = [
                {
                    "quest_id": "qst_theory",
                    "title": "AWS VPC Ağ Güvenliği Çalışması",
                    "description": "AWS resmi dokümantasyonundan VPC Security Groups ve NACL farklarını oku (20 dk).",
                    "xp_reward": 150,
                    "status": "pending",
                    "verified_by": "calendar_sync",
                    "resource_link": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html"
                },
                {
                    "quest_id": "qst_practice",
                    "title": "Docker Compose Dosyası Hazırlama",
                    "description": "FastAPI backend ve Postgres DB barındıran bir docker-compose.yml dosyası yaz ve çalıştır.",
                    "xp_reward": 200,
                    "status": "pending",
                    "verified_by": "github_commit",
                    "resource_link": None
                },
                {
                    "quest_id": "qst_general",
                    "title": "Almanca Kelime Kartları - Duolingo",
                    "description": "Almanca temel selamlaşma ve meslek kelimelerini çalış (10 dk).",
                    "xp_reward": 50,
                    "status": "pending",
                    "verified_by": "manual",
                    "resource_link": "https://www.duolingo.com"
                }
            ]

    # Save to database
    save_daily_quests(user_id, quests)
    return [DailyQuest(**q) for q in quests]


@router.post("/{quest_id}/verify", response_model=QuestVerifyResponse, summary="Görevi tamamlandı olarak işaretle")
async def verify_quest(quest_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Görevi doğrular:
    - Hafta 2'de manual onay desteği aktiftir.
    - Calendar/GitHub entegrasyonu Hafta 3'te ekleneceği için bu kontroller şimdilik manual onaylanır.
    - Başarılı doğrulamada XP kazandırır ve Level Up kontrolü yapar.
    """
    quests = get_daily_quests(user_id)
    if not quests:
        raise HTTPException(status_code=404, detail="Bugünün görev listesi bulunamadı.")

    # Görevi ara
    target_quest = None
    for q in quests:
        if q["quest_id"] == quest_id:
            target_quest = q
            break

    if not target_quest:
        raise HTTPException(status_code=404, detail=f"'{quest_id}' kimlikli görev bulunamadı.")

    if target_quest["status"] == "completed":
        raise HTTPException(status_code=400, detail="Bu görev zaten tamamlanmış.")

    # Görevi tamamlandı yap
    target_quest["status"] = "completed"
    target_quest["completed_at"] = datetime.utcnow().isoformat() + "Z"
    save_daily_quests(user_id, quests)

    # Kullanıcı profilini güncelle (XP ekle)
    user_data = get_user(user_id)
    if not user_data:
        # Auto-initialize profile for users that didn't go through onboarding (e.g. test users)
        user_data = {"user_id": user_id, "level": 1, "xp": 0, "next_level_xp": 1000, "rpgState": {"level": 1, "xp": 0}}
        save_user(user_id, user_data)

    rpg_state = user_data.get("rpgState", {
        "level": 1,
        "xp": 0,
        "next_level_xp": 1000,
        "title": "Novice Seeker"
    })

    xp_reward = target_quest["xp_reward"]
    current_xp = rpg_state.get("xp", 0) + xp_reward
    level = rpg_state.get("level", 1)
    next_level_xp = rpg_state.get("next_level_xp", level * 1000)
    level_up = False

    # Level Up Progression Loop
    while current_xp >= next_level_xp:
        current_xp -= next_level_xp
        level += 1
        next_level_xp = level * 1000
        level_up = True

    # Update title based on level
    title = "Novice Seeker"
    if level == 2:
        title = "Simulation Apprentice"
    elif level == 3:
        title = "Reality Architect"
    elif level >= 4:
        title = "AlterLife Master"

    rpg_state["level"] = level
    rpg_state["xp"] = current_xp
    rpg_state["next_level_xp"] = next_level_xp
    rpg_state["title"] = title

    # ── Energy Drain ─────────────────────────────────────────────────────────
    # Her görev tamamlandığında 10 Energy tüketilir
    current_energy = rpg_state.get("energy", 100)
    current_focus = rpg_state.get("focus", 100)
    energy_cost = 10
    new_energy = max(0, current_energy - energy_cost)
    new_focus = max(0, current_focus - 5)  # Focus daha yavaş düşer
    rpg_state["energy"] = new_energy
    rpg_state["focus"] = new_focus
    if "max_energy" not in rpg_state:
        rpg_state["max_energy"] = 100
    if "max_focus" not in rpg_state:
        rpg_state["max_focus"] = 100

    user_data["rpgState"] = rpg_state
    save_user(user_id, user_data)

    # Düşük enerji uyarısı
    rest_warning = None
    if new_energy <= 20:
        rest_warning = "⚠️ Enerjin çok düşük! Dinlenmen ve Focus'unu yenilemen önerilir. (/user/rest)"

    return {
        "quest_id": quest_id,
        "status": "completed",
        "xp_earned": xp_reward,
        "new_total_xp": current_xp,
        "level_up": level_up,
        "energy_remaining": new_energy,
        "focus_remaining": new_focus,
        "energy_cost": energy_cost,
        "rest_warning": rest_warning,
    }
