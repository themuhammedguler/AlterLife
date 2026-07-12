"""
Agent Training Dataset – 12 Gerçekçi Türkiye Senaryosu
Her senaryo: kullanıcı profili + beklenen çıktı + kalite değerlendirme fonksiyonu
"""
from typing import Dict, Any, List, Callable

# ── Training Scenarios ────────────────────────────────────────────────────────

TRAINING_SCENARIOS: List[Dict[str, Any]] = [
    # ── 1. Almanya Yazılım Göçü ───────────────────────────────────────────────
    {
        "scenario_id": "sc_001",
        "name": "Almanya'ya Yazılım Mühendisi Göçü",
        "user_profile": {
            "age": "28", "city": "İstanbul", "field": "Yazılım Geliştirme",
            "status": "Çalışıyor", "freeGoal": "2 yıl içinde Almanya'da yazılım mühendisi olarak çalışmak",
            "workPrefs": ["uzaktan", "teknoloji"], "risk_tolerance": "medium",
            "monthly_savings": 800, "level": 3, "xp": 1400,
            "known_skills": ["Python", "Docker"], "languages": {"Turkish": "native", "English": "B2"},
        },
        "expected_archetype": "Planlayıcı",
        "expected_agents": ["profile_analyzer", "career_coach", "migration", "skill_gap", "timeline", "financial"],
        "expected_milestones_keywords": ["AWS", "Almanca", "Mavi Kart", "vize", "mülakat"],
        "expected_metric_ranges": {"financial_plan_months": (18, 36), "skill_gap_count": (2, 5)},
    },
    # ── 2. SaaS Startup Bootstrap ─────────────────────────────────────────────
    {
        "scenario_id": "sc_002",
        "name": "SaaS Startup Bootstrap",
        "user_profile": {
            "age": "31", "city": "Ankara", "field": "Ürün Yönetimi",
            "status": "Çalışıyor", "freeGoal": "Kendi SaaS ürünümü kurup ilk 100 ödeyiciye ulaşmak",
            "workPrefs": ["girişimcilik", "remote"], "risk_tolerance": "high",
            "monthly_savings": 1500, "level": 4, "xp": 2100,
            "known_skills": ["Product Management", "JavaScript"], "languages": {"Turkish": "native", "English": "C1"},
        },
        "expected_archetype": "Riskçi",
        "expected_agents": ["profile_analyzer", "financial", "career_coach", "timeline", "scenario"],
        "expected_milestones_keywords": ["MVP", "kullanıcı", "gelir", "pazarlama", "yatırım"],
        "expected_metric_ranges": {"financial_plan_months": (6, 18), "risk_score": (70, 100)},
    },
    # ── 3. Freelance Geçişi ───────────────────────────────────────────────────
    {
        "scenario_id": "sc_003",
        "name": "Kurumsal İşten Freelance Geçiş",
        "user_profile": {
            "age": "34", "city": "İzmir", "field": "UI/UX Tasarım",
            "status": "Çalışıyor", "freeGoal": "Kurumsal işimden ayrılıp tam zamanlı freelance çalışmak",
            "workPrefs": ["bağımsızlık", "yaratıcılık"], "risk_tolerance": "medium",
            "monthly_savings": 600, "level": 2, "xp": 950,
            "known_skills": ["Figma", "Prototyping"], "languages": {"Turkish": "native", "English": "B1"},
        },
        "expected_archetype": "Hayalci",
        "expected_agents": ["profile_analyzer", "financial", "wellbeing", "timeline", "career_coach"],
        "expected_milestones_keywords": ["portföy", "müşteri", "fiyatlandırma", "sözleşme", "acil fon"],
        "expected_metric_ranges": {"financial_plan_months": (9, 24), "wellbeing_score": (40, 70)},
    },
    # ── 4. Kariyer Geçişi: Yazılım → PM ──────────────────────────────────────
    {
        "scenario_id": "sc_004",
        "name": "Yazılım Geliştiriciden Ürün Yöneticisine Geçiş",
        "user_profile": {
            "age": "30", "city": "İstanbul", "field": "Backend Geliştirme",
            "status": "Çalışıyor", "freeGoal": "Mevcut şirkette PM pozisyonuna geçmek veya yeni bir şirkete PM olarak girmek",
            "workPrefs": ["liderlik", "teknoloji"], "risk_tolerance": "low",
            "monthly_savings": 1200, "level": 3, "xp": 1800,
            "known_skills": ["Python", "FastAPI", "Docker"], "languages": {"Turkish": "native", "English": "C1"},
        },
        "expected_archetype": "Planlayıcı",
        "expected_agents": ["profile_analyzer", "career_coach", "skill_gap", "timeline"],
        "expected_milestones_keywords": ["roadmap", "stakeholder", "sertifika", "A/B testi", "kullanıcı araştırması"],
        "expected_metric_ranges": {"transition_months": (6, 18), "skill_gap_count": (3, 6)},
    },
    # ── 5. Yüksek Lisans Yurt Dışı ────────────────────────────────────────────
    {
        "scenario_id": "sc_005",
        "name": "Yurt Dışı Yüksek Lisans (Avrupa)",
        "user_profile": {
            "age": "24", "city": "Bursa", "field": "Bilgisayar Mühendisliği",
            "status": "Öğrenci", "freeGoal": "Almanya veya Hollanda'da CS master yapmak",
            "workPrefs": ["akademi", "araştırma"], "risk_tolerance": "medium",
            "monthly_savings": 200, "level": 1, "xp": 400,
            "known_skills": ["Python", "Machine Learning Temelleri"], "languages": {"Turkish": "native", "English": "B2", "German": "A1"},
        },
        "expected_archetype": "Hayalci",
        "expected_agents": ["profile_analyzer", "migration", "financial", "skill_gap", "timeline"],
        "expected_milestones_keywords": ["IELTS", "başvuru", "burs", "dil", "vize"],
        "expected_metric_ranges": {"preparation_months": (12, 24)},
    },
    # ── 6. Uzaktan Çalışma Geçişi ─────────────────────────────────────────────
    {
        "scenario_id": "sc_006",
        "name": "Ofis İşinden Tam Uzaktan Çalışmaya Geçiş",
        "user_profile": {
            "age": "32", "city": "Trabzon", "field": "Veri Analizi",
            "status": "Çalışıyor", "freeGoal": "Yabancı şirkete remote data analyst olarak girmek",
            "workPrefs": ["uzaktan", "veri"], "risk_tolerance": "low",
            "monthly_savings": 500, "level": 2, "xp": 700,
            "known_skills": ["SQL", "Python", "Tableau"], "languages": {"Turkish": "native", "English": "B2"},
        },
        "expected_archetype": "Pratik",
        "expected_agents": ["profile_analyzer", "career_coach", "skill_gap", "timeline", "financial"],
        "expected_milestones_keywords": ["portföy", "LinkedIn", "yabancı", "mülakat", "SQL"],
        "expected_metric_ranges": {"transition_months": (3, 12)},
    },
    # ── 7. Sağlık Krizi + Kariyer Pause ──────────────────────────────────────
    {
        "scenario_id": "sc_007",
        "name": "Burnout Sonrası Kariyer Yeniden Yapılanması",
        "user_profile": {
            "age": "35", "city": "İstanbul", "field": "Yazılım Mimarisi",
            "status": "Çalışıyor", "freeGoal": "Burnout'tan kurtulup anlamlı bir işe geçmek",
            "workPrefs": ["denge", "anlam"], "risk_tolerance": "low",
            "monthly_savings": 2000, "level": 5, "xp": 3200,
            "known_skills": ["Python", "Docker", "AWS", "System Design"],
            "stress_level": 85, "happiness": 30,
            "languages": {"Turkish": "native", "English": "C2"},
        },
        "expected_archetype": "Planlayıcı",
        "expected_agents": ["profile_analyzer", "wellbeing", "financial", "career_coach", "timeline"],
        "expected_milestones_keywords": ["mola", "terapi", "anlam", "iş-yaşam", "yenileme"],
        "expected_metric_ranges": {"wellbeing_score": (10, 40), "burnout_risk": (70, 100)},
    },
    # ── 8. Mavi Yaka → Beyaz Yaka ────────────────────────────────────────────
    {
        "scenario_id": "sc_008",
        "name": "Mavi Yakardan Yazılım Geliştiricisine",
        "user_profile": {
            "age": "26", "city": "Gaziantep", "field": "Üretim / Fabrika",
            "status": "Çalışıyor", "freeGoal": "Kendi kendime yazılım öğrenip yazılımcı olarak işe girmek",
            "workPrefs": ["öğrenme", "teknoloji"], "risk_tolerance": "medium",
            "monthly_savings": 150, "level": 1, "xp": 100,
            "known_skills": [], "languages": {"Turkish": "native", "English": "A2"},
        },
        "expected_archetype": "Hayalci",
        "expected_agents": ["profile_analyzer", "career_coach", "skill_gap", "timeline", "wellbeing"],
        "expected_milestones_keywords": ["Python", "proje", "GitHub", "bootcamp", "portfolyo"],
        "expected_metric_ranges": {"transition_months": (12, 30), "skill_gap_count": (5, 10)},
    },
    # ── 9. Kanada Göçü ────────────────────────────────────────────────────────
    {
        "scenario_id": "sc_009",
        "name": "Kanada'ya Yazılım Göçü (Express Entry)",
        "user_profile": {
            "age": "33", "city": "Ankara", "field": "Full-Stack Geliştirme",
            "status": "Çalışıyor", "freeGoal": "Kanada Express Entry ile göç etmek",
            "workPrefs": ["aile", "güvenlik"], "risk_tolerance": "low",
            "monthly_savings": 1000, "level": 4, "xp": 2400,
            "known_skills": ["React", "Node.js", "PostgreSQL"], "languages": {"Turkish": "native", "English": "C1"},
            "family_status": "evli, 1 çocuk",
        },
        "expected_archetype": "Pratik",
        "expected_agents": ["profile_analyzer", "migration", "financial", "timeline", "wellbeing"],
        "expected_milestones_keywords": ["IELTS", "EE puan", "referans mektubu", "vergi", "yerleşim"],
        "expected_metric_ranges": {"preparation_months": (18, 48)},
    },
    # ── 10. Sosyal Girişim ────────────────────────────────────────────────────
    {
        "scenario_id": "sc_010",
        "name": "Eğitim Odaklı Sosyal Girişim",
        "user_profile": {
            "age": "29", "city": "İzmir", "field": "Eğitim Teknolojisi",
            "status": "Çalışıyor", "freeGoal": "Dezavantajlı gençler için kodlama platformu kurmak",
            "workPrefs": ["anlam", "sosyal etki"], "risk_tolerance": "medium",
            "monthly_savings": 400, "level": 2, "xp": 800,
            "known_skills": ["Python", "React"], "languages": {"Turkish": "native", "English": "B2"},
        },
        "expected_archetype": "Hayalci",
        "expected_agents": ["profile_analyzer", "career_coach", "financial", "timeline", "scenario"],
        "expected_milestones_keywords": ["hibe", "faydalanıcı", "ortaklık", "platform", "etki"],
        "expected_metric_ranges": {"financial_plan_months": (12, 36)},
    },
    # ── 11. Emeklilik Planlaması ──────────────────────────────────────────────
    {
        "scenario_id": "sc_011",
        "name": "Erken Emeklilik (FIRE) Planlaması",
        "user_profile": {
            "age": "38", "city": "İstanbul", "field": "Finans / Yatırım",
            "status": "Çalışıyor", "freeGoal": "50 yaşına kadar mali bağımsızlığa ulaşmak",
            "workPrefs": ["yatırım", "bağımsızlık"], "risk_tolerance": "medium",
            "monthly_savings": 3000, "level": 5, "xp": 4000,
            "known_skills": ["Finansal Modelleme", "Excel"], "languages": {"Turkish": "native", "English": "C1"},
        },
        "expected_archetype": "Planlayıcı",
        "expected_agents": ["profile_analyzer", "financial", "timeline", "wellbeing"],
        "expected_milestones_keywords": ["portföy", "birikim oranı", "pasif gelir", "4% kuralı", "yatırım"],
        "expected_metric_ranges": {"financial_plan_months": (100, 200)},
    },
    # ── 12. Liderlik Geçişi ───────────────────────────────────────────────────
    {
        "scenario_id": "sc_012",
        "name": "Tech Lead'den Yöneticiliğe Geçiş",
        "user_profile": {
            "age": "36", "city": "İstanbul", "field": "Yazılım Mimarisi / Team Lead",
            "status": "Çalışıyor", "freeGoal": "Engineering Manager veya CTO pozisyonuna geçmek",
            "workPrefs": ["liderlik", "etki"], "risk_tolerance": "low",
            "monthly_savings": 2500, "level": 5, "xp": 5000,
            "known_skills": ["Python", "System Design", "Team Leadership"], "languages": {"Turkish": "native", "English": "C2"},
        },
        "expected_archetype": "Pratik",
        "expected_agents": ["profile_analyzer", "career_coach", "skill_gap", "timeline"],
        "expected_milestones_keywords": ["1-on-1", "OKR", "hiring", "strateji", "bütçe"],
        "expected_metric_ranges": {"transition_months": (6, 24)},
    },
]


# ── Quality Evaluation Functions ──────────────────────────────────────────────

def evaluate_agent_output(scenario_id: str, agent_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir agent çıktısını eğitim senaryosuyla karşılaştırır ve kalite skoru döner.
    """
    scenario = next((s for s in TRAINING_SCENARIOS if s["scenario_id"] == scenario_id), None)
    if not scenario:
        return {"score": 0, "error": f"Scenario {scenario_id} not found"}

    score = 0
    feedback = []

    # 1. Output'ta içerik var mı?
    if not output or (isinstance(output, dict) and not any(output.values())):
        return {"score": 0, "feedback": ["Boş çıktı"]}

    # 2. Beklenen milestone keyword'leri var mı?
    output_str = str(output).lower()
    keyword_hits = 0
    expected_keywords = scenario.get("expected_milestones_keywords", [])
    for kw in expected_keywords:
        if kw.lower() in output_str:
            keyword_hits += 1
    keyword_score = int((keyword_hits / max(1, len(expected_keywords))) * 50)
    score += keyword_score
    feedback.append(f"Keyword eşleşmesi: {keyword_hits}/{len(expected_keywords)} → +{keyword_score} puan")

    # 3. Türkçe mi? (Temel kontrol)
    turkish_chars = sum(1 for c in output_str if c in "çğışöüÇĞİŞÖÜ")
    if turkish_chars > 3:
        score += 20
        feedback.append("Türkçe içerik tespit edildi → +20 puan")
    else:
        feedback.append("Türkçe içerik yetersiz → +0 puan")

    # 4. Uzunluk yeterli mi? (At least 50 chars)
    if len(output_str) > 50:
        score += 15
        feedback.append("Yeterli uzunluk → +15 puan")
    else:
        feedback.append("Çıktı çok kısa → +0 puan")

    # 5. Hata var mı?
    if output.get("error"):
        score = max(0, score - 30)
        feedback.append(f"Hata tespit edildi: {output.get('error')} → -30 puan")
    else:
        score += 15
        feedback.append("Hatasız çıktı → +15 puan")

    return {
        "scenario_id": scenario_id,
        "agent": agent_name,
        "score": min(100, score),
        "max_score": 100,
        "feedback": feedback,
        "keyword_hits": keyword_hits,
        "total_keywords": len(expected_keywords),
    }


def get_scenario_by_profile(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kullanıcı profiline en yakın eğitim senaryosunu döner (referans için).
    """
    goal = user_profile.get("freeGoal", "").lower()
    field = user_profile.get("field", "").lower()

    if any(k in goal for k in ["almanya", "berlin", "germany"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_001")
    if any(k in goal for k in ["kanada", "canada"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_009")
    if any(k in goal for k in ["startup", "saas", "girişim"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_002")
    if any(k in goal for k in ["freelance", "serbest"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_003")
    if any(k in goal for k in ["yüksek lisans", "master", "master's"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_005")
    if any(k in goal for k in ["uzaktan", "remote"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_006")
    if any(k in goal for k in ["burnout", "anlam", "mola"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_007")
    if any(k in goal for k in ["emeklilik", "fire", "bağımsız"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_011")
    if any(k in goal for k in ["lider", "manager", "cto", "yönetici"]):
        return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_012")

    # Default generic
    return next(s for s in TRAINING_SCENARIOS if s["scenario_id"] == "sc_006")
