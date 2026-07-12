"""
CareerCoachAgent – Kişisel kariyer yol haritası, skill gap analizi, sıralı öğrenme planı
"""
import os, json
from typing import Dict, Any, List

GEMINI_SYSTEM = "Sen Türkiye ve uluslararası teknoloji sektörü için kariyer koçusun. Kişiselleştirilmiş, somut ve uygulanabilir tavsiyeler ver. SADECE JSON döndür."

SKILL_PREREQUISITES = {
    "cloud_architect": ["AWS Fundamentals", "Docker", "Linux", "Networking"],
    "product_manager": ["User Research", "Data Analysis", "Roadmapping", "Stakeholder Management"],
    "ml_engineer": ["Python", "Statistics", "Machine Learning", "Deep Learning", "MLOps"],
    "engineering_manager": ["Team Leadership", "1-on-1s", "OKR Setting", "Hiring", "Budget Planning"],
    "fullstack_developer": ["HTML/CSS", "JavaScript", "React", "Node.js", "Database", "Docker"],
    "data_analyst": ["SQL", "Python", "Excel", "Visualization", "Statistics"],
    "mobile_developer": ["Swift/Kotlin", "React Native", "Mobile UX", "App Store Deployment"],
    "devops_engineer": ["Linux", "Docker", "Kubernetes", "CI/CD", "Terraform", "Monitoring"],
    "freelancer": ["Portföy", "Müşteri İletişimi", "Sözleşme Yönetimi", "Fiyatlandırma", "Pazarlama"],
    "cto": ["System Design", "Architecture", "Team Building", "Strategy", "Fundraising"],
}

def identify_target_role(goal: str) -> str:
    goal_lower = goal.lower()
    if any(k in goal_lower for k in ["cloud", "aws", "azure", "gcp"]): return "cloud_architect"
    if any(k in goal_lower for k in ["product manager", "pm", "ürün yönetici"]): return "product_manager"
    if any(k in goal_lower for k in ["machine learning", "ml", "ai", "yapay zeka"]): return "ml_engineer"
    if any(k in goal_lower for k in ["engineering manager", "em", "mühendislik yönetici"]): return "engineering_manager"
    if any(k in goal_lower for k in ["fullstack", "full stack", "full-stack"]): return "fullstack_developer"
    if any(k in goal_lower for k in ["data analyst", "veri analizi"]): return "data_analyst"
    if any(k in goal_lower for k in ["devops", "platform", "altyapı"]): return "devops_engineer"
    if any(k in goal_lower for k in ["freelance", "serbest", "bağımsız"]): return "freelancer"
    if any(k in goal_lower for k in ["cto", "genel müdür", "yönetici"]): return "cto"
    return "fullstack_developer"

def create_career_roadmap(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any], skill_nodes: List[Dict] = None) -> Dict[str, Any]:
    goal = user_profile.get("freeGoal", "kariyer hedefi")
    known_skills = user_profile.get("known_skills", [])
    if skill_nodes:
        unlocked_skills = [n["name"] for n in skill_nodes if n.get("is_unlocked") and n.get("level", 0) >= 1]
        known_skills = list(set(known_skills + unlocked_skills))

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM)
            prompt = f"""
Kullanıcı Bilgileri:
- Hedef: {goal}
- Mevcut Beceriler: {', '.join(known_skills) if known_skills else 'Yok'}
- Arketip: {profile_analysis.get('archetype', '?')}
- Öğrenme Stili: {profile_analysis.get('learning_style', '?')}
- Risk Toleransı: {profile_analysis.get('risk_tolerance', 'medium')}
- Şehir: {user_profile.get('city', '?')}
- Aciliyet Skoru: {profile_analysis.get('urgency_score', 5)}/10

Few-shot örnek çıktı:
{{
  "target_role": "Cloud Architect",
  "skill_gap": [
    {{"skill": "Kubernetes", "priority": 1, "reason": "Hedef pozisyon için kritik", "est_weeks": 6, "resource": "KodeKloud CKA Kursu"}},
    {{"skill": "Terraform", "priority": 2, "reason": "Infrastructure as Code zorunlu", "est_weeks": 4, "resource": "HashiCorp Resmi Dokümanlar"}}
  ],
  "roadmap_phases": [
    {{"phase": 1, "title": "Temel Sertifikasyon", "duration_weeks": 8, "milestones": ["AWS SAA sınavını geç"], "resources": ["A Cloud Guru"]}},
    {{"phase": 2, "title": "Uygulama Projeleri", "duration_weeks": 12, "milestones": ["3 proje bitir"], "resources": ["GitHub"]}}
  ],
  "quick_start_action": "Bu hafta yapabileceğin 1 şey",
  "estimated_total_weeks": 24,
  "job_market_insight": "Bu role olan talep ve maaş beklentisi",
  "linkedin_keywords": ["keyword1", "keyword2", "keyword3"]
}}

Kullanıcı için bu formatı doldur:
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[CareerCoach] Gemini failed: {e}")

    # Mock fallback
    target_role = identify_target_role(goal)
    required = SKILL_PREREQUISITES.get(target_role, ["Python", "Git", "Docker"])
    gaps = [s for s in required if not any(k.lower() in s.lower() or s.lower() in k.lower() for k in known_skills)]

    skill_gap = [{"skill": s, "priority": i+1, "reason": "Hedef pozisyon için gerekli", "est_weeks": 4+i*2, "resource": f"{s} Resmi Dokümanları"} for i, s in enumerate(gaps[:5])]
    total_weeks = sum(g["est_weeks"] for g in skill_gap) + 4

    return {
        "target_role": target_role.replace("_", " ").title(),
        "skill_gap": skill_gap,
        "roadmap_phases": [
            {"phase": 1, "title": "Temel Beceri İnşası", "duration_weeks": total_weeks // 3, "milestones": [f"{gaps[0]} öğren" if gaps else "Temelleri pekiştir"], "resources": ["Udemy", "YouTube"]},
            {"phase": 2, "title": "Uygulama & Proje", "duration_weeks": total_weeks // 3, "milestones": ["GitHub'a 2 proje yükle", "Portfolio hazırla"], "resources": ["GitHub", "Personal Projects"]},
            {"phase": 3, "title": "İş Başvurusu", "duration_weeks": total_weeks // 3, "milestones": ["10 başvuru yap", "3 mülakata gir"], "resources": ["LinkedIn", "Kariyer.net"]},
        ],
        "quick_start_action": f"Bugün '{gaps[0] if gaps else 'hedefin'}' için 30 dakika YouTube videosu izle ve not al",
        "estimated_total_weeks": total_weeks,
        "job_market_insight": f"{target_role.title()} pozisyonları için Türkiye'de talep artıyor. Uzaktan çalışma fırsatları da mevcut.",
        "linkedin_keywords": required[:5],
        "source": "mock",
    }
