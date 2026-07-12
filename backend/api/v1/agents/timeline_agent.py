"""
TimelineAgent – Gerçekçi hedef zaman tahmini
Kullanıcının mevcut hızını (XP, görev tamamlama oranı) ölçerek hedef tarih hesaplar.
"""
import os, json
from datetime import date, timedelta
from typing import Dict, Any

GEMINI_SYSTEM = "Sen proje yönetimi ve kariyer planlama uzmanısın. Gerçekçi, veri temelli zaman tahminleri yap. SADECE JSON döndür. Türkçe yaz."

def estimate_timeline(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any], analytics_data: Dict = None) -> Dict[str, Any]:
    level = user_profile.get("level", 1)
    xp = user_profile.get("xp", 0)
    goal = user_profile.get("freeGoal", "hedef")
    completed_quests = user_profile.get("completed_quests", 0)
    active_days = user_profile.get("active_days", 5)
    archetype = profile_analysis.get("archetype", "Pratik")
    urgency = profile_analysis.get("urgency_score", 5)
    monthly_savings = user_profile.get("monthly_savings", 500)

    # XP velocity: estimated weekly XP gain
    weekly_xp = max(50, (xp / max(1, level * 4)) * 7)
    daily_hours_available = 2.0 if active_days >= 5 else 1.0 if active_days >= 3 else 0.5

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM)
            prompt = f"""
Kullanıcı İlerleme Metrikleri:
- Hedef: {goal}
- Seviye: {level}, XP: {xp}
- Tamamlanan Görev: {completed_quests}
- Haftalık Aktif Gün: {active_days}
- Tahmini Haftalık XP Kazanımı: {weekly_xp:.0f}
- Aylık Birikim: {monthly_savings}$
- Arketip: {archetype}, Aciliyet Skoru: {urgency}/10

Gerçekçi zaman tahmini:
- current_pace_months: Şu anki hızla kaç ayda bitir?
- optimized_pace_months: Optimum hız ile kaç ayda?
- aggressive_pace_months: Maksimum yoğunlukla kaç ayda?
- estimated_completion_date: current_pace ile tahmini bitiş tarihi (YYYY-MM formatı)
- pace_comparison: [{{ "label": "Şu An", "months": X, "risk": "Düşük/Orta/Yüksek" }}]
- bottlenecks: [En büyük 3 darboğaz]
- acceleration_tips: [Hızlanmak için 3 somut öneri]
- milestone_schedule: [{{ "milestone": "...", "target_month": 3 }}]
- confidence_score: Bu tahminin güven skoru (0-100)
- reality_check: Gerçek bir değerlendirme (1-2 cümle, samimi ol)
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[TimelineAgent] Gemini failed: {e}")

    # Heuristic mock
    # Base months: depends on goal complexity
    goal_lower = goal.lower()
    base_months = 24
    if any(k in goal_lower for k in ["almanya", "kanada", "göç", "vize"]): base_months = 18
    elif any(k in goal_lower for k in ["startup", "girişim"]): base_months = 12
    elif any(k in goal_lower for k in ["freelance", "serbest"]): base_months = 9
    elif any(k in goal_lower for k in ["sertifika", "kurs"]): base_months = 4

    # Adjust by level
    pace_factor = max(0.5, 1.0 - (level * 0.05))
    current_pace = max(3, int(base_months * pace_factor * (1.0 if active_days >= 5 else 1.4)))
    optimized = max(2, int(current_pace * 0.75))
    aggressive = max(1, int(current_pace * 0.55))

    completion_date = (date.today() + timedelta(days=current_pace * 30)).strftime("%Y-%m")
    burnout_risk = "Yüksek" if aggressive < 4 else "Orta" if aggressive < 8 else "Düşük"

    return {
        "current_pace_months": current_pace,
        "optimized_pace_months": optimized,
        "aggressive_pace_months": aggressive,
        "estimated_completion_date": completion_date,
        "pace_comparison": [
            {"label": "Şu An", "months": current_pace, "risk": "Düşük"},
            {"label": "Optimize", "months": optimized, "risk": "Orta"},
            {"label": "Yoğun", "months": aggressive, "risk": burnout_risk},
        ],
        "bottlenecks": [
            f"Haftalık yalnızca {active_days} aktif gün — daha fazlası hızlandırır",
            f"Mevcut seviye {level} — XP kazanım hızı artırılabilir",
            "Belirsiz kısa vadeli alt hedefler motivasyon düşürüyor",
        ],
        "acceleration_tips": [
            "Her gün 1 görev tamamlamayı zorunlu kıl (küçük olsa da)",
            f"Haftalık hedefleri Pazar günü yazıp Cuma günü gözden geçir",
            f"Bir hesap verebilirlik partneri bul — haftalık ilerleme paylaş",
        ],
        "milestone_schedule": [
            {"milestone": "Temel becerileri edinme", "target_month": current_pace // 4},
            {"milestone": "İlk somut proje / çıktı", "target_month": current_pace // 2},
            {"milestone": "Hedefe ulaşma", "target_month": current_pace},
        ],
        "confidence_score": max(40, min(90, 50 + level * 5 + active_days * 3 - (7 - active_days) * 5)),
        "reality_check": f"Şu anki hızınla {current_pace} ayda ulaşabilirsin. Bu makul ama {'biraz hızlandırmak seni öne geçirir' if active_days < 5 else 'tutarlılığını korudu'}.",
        "source": "mock",
    }
