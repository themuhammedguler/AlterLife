"""
ProfileAnalyzerAgent – Kullanıcıyı derinlemesine tanır
Kişilik arketipi, motivasyon kaynakları, risk toleransı, öğrenme stili belirler.
Bu bilgi OrchestratorAgent tarafından diğer agent'lara aktarılır.
"""

import os
import json
from typing import Dict, Any, Optional

PERSONALITY_ARCHETYPES = {
    "Riskçi": "Yüksek riskli yüksek ödüllü yolları tercih eder. Hızlı hareket eder, startup/girişim odaklı.",
    "Planlayıcı": "Adım adım, sistematik ilerlemeyi sever. Risk almadan önce iyice araştırır.",
    "Hayalci": "Büyük hayaller kurar ama planlamada zorlanabilir. İlham ve anlam odaklı.",
    "Pratik": "Sonuca odaklıdır. Duygusal kararlar değil, veri temelli seçimler yapar.",
}

MOTIVATION_TYPES = ["Para / Finansal Güvenlik", "Özgürlük / Bağımsızlık", "Prestij / Tanınma", "Anlam / Sosyal Etki", "Aile / İstikrar"]
LEARNING_STYLES = ["Videolardan", "Yaparak / Uygulayarak", "Kitaptan / Okuyarak", "Mentörden"]

GEMINI_SYSTEM_INSTRUCTION = """
Sen AlterLife'ın Profil Analiz Uzmanısın.
Kullanıcının verdiği bilgilere dayanarak derin bir psikolojik ve kariyer profili çıkarıyorsun.
Her zaman Türkçe yaz. Samimi, anlayışlı ve motive edici bir dil kullan.
SADECE JSON döndür, başka bir şey yazma.
"""

MOCK_PROFILES = {
    "Riskçi": {
        "archetype": "Riskçi",
        "archetype_description": "Hızlı hareket eden, yüksek ödül arayan bir profil. Belirsizlikten korkmuyorsun, aksine onu fırsat olarak görüyorsun.",
        "motivation_primary": "Özgürlük / Bağımsızlık",
        "motivation_secondary": "Prestij / Tanınma",
        "learning_style": "Yaparak / Uygulayarak",
        "risk_tolerance": "high",
        "urgency_score": 9,
        "strengths": ["Hızlı karar verme", "İnovasyon odaklı düşünce", "Girişimcilik ruhu"],
        "blind_spots": ["Uzun vadeli planlama", "Finansal güvenlik tamponu", "Stres yönetimi"],
        "recommended_agents": ["financial", "career_coach", "timeline", "scenario"],
        "motivational_message": "Hız senin gücün — ama sağlam bir temel olmadan hız sadece çöküşü hızlandırır. Finansal güvenliğini oluştururken hedefine koş.",
    },
    "Planlayıcı": {
        "archetype": "Planlayıcı",
        "archetype_description": "Sistematik düşünen, adım adım ilerleyen birisin. Her kararın önce artı-eksilerini tartıyorsun.",
        "motivation_primary": "Para / Finansal Güvenlik",
        "motivation_secondary": "Aile / İstikrar",
        "learning_style": "Kitaptan / Okuyarak",
        "risk_tolerance": "low",
        "urgency_score": 5,
        "strengths": ["Detaylı analiz", "Sürdürülebilir ilerleme", "Risk yönetimi"],
        "blind_spots": ["Aşırı düşünme (paralysis)", "Fırsatları kaçırma riski", "Mükemmeliyetçilik"],
        "recommended_agents": ["career_coach", "skill_gap", "migration", "timeline", "financial"],
        "motivational_message": "Planlamak gücündür — ama en iyi plan, uygulamaya başlayan plandır. Bugün küçük bir adım at.",
    },
    "Hayalci": {
        "archetype": "Hayalci",
        "archetype_description": "Büyük vizyonlara sahip, ilham odaklı birisin. Anlam ve etki seni motive ediyor.",
        "motivation_primary": "Anlam / Sosyal Etki",
        "motivation_secondary": "Özgürlük / Bağımsızlık",
        "learning_style": "Videolardan",
        "risk_tolerance": "medium",
        "urgency_score": 6,
        "strengths": ["Büyük resmi görme", "Yaratıcılık", "İnsanları motive etme"],
        "blind_spots": ["Somut adım planları", "Finansal disiplin", "Hedef süre gerçekçiliği"],
        "recommended_agents": ["career_coach", "financial", "wellbeing", "timeline", "scenario"],
        "motivational_message": "Hayallerin gerçek — ama hayalden hedefe giden köprüyü adım adım inşa etmek gerekiyor. İlk küçük kazanımını hedefle.",
    },
    "Pratik": {
        "archetype": "Pratik",
        "archetype_description": "Sonuç odaklı, verimlilik-takıntılı birisin. Ne işe yarıyorsa onu yaparsın.",
        "motivation_primary": "Para / Finansal Güvenlik",
        "motivation_secondary": "Prestij / Tanınma",
        "learning_style": "Yaparak / Uygulayarak",
        "risk_tolerance": "medium",
        "urgency_score": 7,
        "strengths": ["Verimlilik", "Net hedef koyma", "Adapte olma"],
        "blind_spots": ["Uzun vadeli anlam sorgulaması", "İlişki yönetimi", "Yaratıcılık alanı bırakma"],
        "recommended_agents": ["skill_gap", "career_coach", "migration", "timeline"],
        "motivational_message": "Verimliliğin en büyük silahın. Ama bazen durup 'Neden?' sorusunu sormak, 'Nasıl?'dan daha değerli olabilir.",
    },
}


def _determine_archetype_heuristic(user_profile: Dict[str, Any]) -> str:
    """Risk toleransı ve hedef anahtar kelimelerine göre arketip tahmini."""
    risk = user_profile.get("risk_tolerance", "medium")
    goal = (user_profile.get("freeGoal", "") + " " + user_profile.get("field", "")).lower()

    if risk == "high" or any(k in goal for k in ["startup", "girişim", "freelance", "serbest"]):
        return "Riskçi"
    if risk == "low" or any(k in goal for k in ["planlama", "sistematik", "güvenli", "istikrar"]):
        return "Planlayıcı"
    if any(k in goal for k in ["anlam", "etki", "hayal", "sosyal", "eğitim"]):
        return "Hayalci"
    return "Pratik"


def analyze_user_profile(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kullanıcı profilini analiz eder. Önce Gemini, yoksa mock.
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
            )
            prompt = f"""
Kullanıcı Profili:
- Yaş: {user_profile.get('age', '?')}
- Şehir: {user_profile.get('city', '?')}
- Alan: {user_profile.get('field', '?')}
- Durum: {user_profile.get('status', '?')}
- Ana Hedef: {user_profile.get('freeGoal', '?')}
- Çalışma Tercihleri: {', '.join(user_profile.get('workPrefs', []))}
- Bilinen Beceriler: {', '.join(user_profile.get('known_skills', []))}
- Aylık Birikim: {user_profile.get('monthly_savings', '?')} USD
- Seviye: {user_profile.get('level', 1)}, XP: {user_profile.get('xp', 0)}

Bu kullanıcı için kapsamlı bir profil analizi yap. Şu alanları doldur:
- archetype: "Riskçi" | "Planlayıcı" | "Hayalci" | "Pratik"
- archetype_description: Kişiye özel 1-2 cümle
- motivation_primary: Ana motivasyon kaynağı
- motivation_secondary: İkincil motivasyon
- learning_style: "Videolardan" | "Yaparak" | "Kitaptan" | "Mentörden"
- risk_tolerance: "low" | "medium" | "high"
- urgency_score: 1-10 (bu hedefe ne kadar acil odaklanmalı)
- strengths: [3 güçlü yön]
- blind_spots: [3 gelişim alanı]
- recommended_agents: ["financial", "career_coach", "wellbeing", "migration", "skill_gap", "timeline", "scenario"] listesinden en uygun 3-5'ini seç
- motivational_message: Kişiye özel motivasyon mesajı (1-2 cümle, Türkçe)

Örnek few-shot çıktı:
{{
  "archetype": "Planlayıcı",
  "archetype_description": "Sistematik ilerlemeyi seven, her adımı ölçen birisin.",
  "motivation_primary": "Para / Finansal Güvenlik",
  "motivation_secondary": "Aile / İstikrar",
  "learning_style": "Kitaptan / Okuyarak",
  "risk_tolerance": "low",
  "urgency_score": 7,
  "strengths": ["Analitik düşünce", "Sabırlı ilerleme", "Risk yönetimi"],
  "blind_spots": ["Aşırı planlama", "Mükemmeliyetçilik", "Hızlı aksiyon alma"],
  "recommended_agents": ["career_coach", "skill_gap", "migration", "financial"],
  "motivational_message": "Adım adım ilerlemek yavaş görünür ama en sağlam yol odur."
}}
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[ProfileAnalyzer] Gemini failed: {e}. Using heuristic mock.")

    # Heuristic mock fallback
    archetype = _determine_archetype_heuristic(user_profile)
    result = dict(MOCK_PROFILES[archetype])

    # Personalize the motivational message
    name = user_profile.get("display_name", "")
    goal = user_profile.get("freeGoal", "hedefin")
    result["motivational_message"] = result["motivational_message"].replace("hedefine", f"'{goal}' hedefine")
    result["source"] = "heuristic_mock"
    return result
