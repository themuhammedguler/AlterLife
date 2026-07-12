"""
SkillGapAgent – Kritik beceri boşluğu analizi, sıralı öğrenme önerileri
"""
import os, json
from typing import Dict, Any, List

GEMINI_SYSTEM = "Sen yazılım ve teknoloji eğitimi alanında uzman bir kariyer danışmanısın. Skill gap analizini somut ve önceliklendirilmiş biçimde sun. SADECE JSON döndür. Türkçe yaz."

URGENCY_MAP = {"critical": "🔴 Kritik", "high": "🟠 Yüksek", "medium": "🟡 Orta", "low": "🟢 Düşük"}

def analyze_skill_gaps(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any], skill_nodes: List[Dict] = None) -> Dict[str, Any]:
    goal = user_profile.get("freeGoal", "kariyer hedefi")
    known = set(k.lower() for k in user_profile.get("known_skills", []))
    if skill_nodes:
        unlocked = {n["name"].lower() for n in skill_nodes if n.get("level", 0) >= 2}
        known = known | unlocked

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM)
            prompt = f"""
Kullanıcı Profili:
- Hedef: {goal}
- Mevcut Beceriler: {', '.join(known) if known else 'Temel düzey, belirsiz'}
- Arketip: {profile_analysis.get('archetype', '?')}
- Öğrenme Stili: {profile_analysis.get('learning_style', '?')}

Skill gap analizi yap ve şunu döndür:
{{
  "total_gaps_found": 5,
  "critical_gaps": [
    {{
      "skill": "Skill Adı",
      "urgency": "critical|high|medium|low",
      "reason": "Neden öncelikli?",
      "learning_path": [
        {{ "step": 1, "action": "Ne yap", "resource": "Kaynak adı", "est_hours": 20 }}
      ],
      "time_to_proficiency_weeks": 6
    }}
  ],
  "learning_sequence": ["Önce bunu öğren", "Sonra bunu", "En son bunu"],
  "total_est_weeks": 24,
  "study_plan": {{
    "daily_hours": 1.5,
    "sessions_per_week": 5,
    "completion_in_weeks": 24
  }},
  "certification_suggestions": [{{ "name": "...", "provider": "...", "cost_usd": 100, "validity_years": 3 }}],
  "quick_win": "Bu hafta 1 saatte öğrenebileceğin şey"
}}
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[SkillGapAgent] Gemini failed: {e}")

    # Heuristic mock
    goal_lower = goal.lower()
    is_cloud = any(k in goal_lower for k in ["cloud", "aws", "azure", "almanya", "germany"])
    is_ml = any(k in goal_lower for k in ["ml", "ai", "makine", "veri"])
    is_frontend = any(k in goal_lower for k in ["frontend", "react", "next", "web"])

    if is_cloud:
        gaps = [
            {"skill": "AWS Solutions Architect", "urgency": "critical", "reason": "Almanya iş ilanlarının %70'i cloud bilgisi istiyor",
             "learning_path": [{"step": 1, "action": "A Cloud Guru SAA kursu", "resource": "acloudguru.com", "est_hours": 40}], "time_to_proficiency_weeks": 8},
            {"skill": "Kubernetes (CKA)", "urgency": "high", "reason": "DevOps pozisyonlarının neredeyse tamamında gerekli",
             "learning_path": [{"step": 1, "action": "KodeKloud CKA Path", "resource": "kodekloud.com", "est_hours": 30}], "time_to_proficiency_weeks": 6},
            {"skill": "Terraform", "urgency": "medium", "reason": "IaC bilgisi maaşı artırıyor",
             "learning_path": [{"step": 1, "action": "HashiCorp Resmi Docs", "resource": "developer.hashicorp.com", "est_hours": 20}], "time_to_proficiency_weeks": 4},
        ]
        sequence = ["AWS Fundamentals", "Docker → Kubernetes", "Terraform", "CI/CD Pipeline", "Monitoring (Prometheus/Grafana)"]
        certs = [{"name": "AWS SAA-C03", "provider": "AWS", "cost_usd": 300, "validity_years": 3}, {"name": "CKA", "provider": "CNCF", "cost_usd": 395, "validity_years": 3}]
    elif is_ml:
        gaps = [
            {"skill": "PyTorch / TensorFlow", "urgency": "critical", "reason": "ML mühendisi pozisyonlarında olmazsa olmaz",
             "learning_path": [{"step": 1, "action": "fast.ai Practical Deep Learning", "resource": "fast.ai", "est_hours": 50}], "time_to_proficiency_weeks": 10},
            {"skill": "MLOps", "urgency": "high", "reason": "Production ML için gerekli, maaş farkı büyük",
             "learning_path": [{"step": 1, "action": "MLOps Zoomcamp", "resource": "github.com/DataTalksClub", "est_hours": 40}], "time_to_proficiency_weeks": 8},
        ]
        sequence = ["Python İleri Seviye", "İstatistik", "Scikit-learn", "PyTorch", "MLOps"]
        certs = [{"name": "Google Professional ML Engineer", "provider": "Google", "cost_usd": 200, "validity_years": 2}]
    else:
        gaps = [
            {"skill": "Next.js / React Advanced", "urgency": "high", "reason": "Modern frontend rollerinde temel gereksinim",
             "learning_path": [{"step": 1, "action": "Next.js Resmi Öğreticisi", "resource": "nextjs.org/learn", "est_hours": 20}], "time_to_proficiency_weeks": 4},
            {"skill": "TypeScript", "urgency": "high", "reason": "Tüm büyük projelerde zorunlu hale geldi",
             "learning_path": [{"step": 1, "action": "TypeScript Handbook", "resource": "typescriptlang.org", "est_hours": 15}], "time_to_proficiency_weeks": 3},
        ]
        sequence = ["JavaScript İleri", "TypeScript", "React/Next.js", "Testing (Jest/Cypress)", "Deployment (Vercel/Docker)"]
        certs = [{"name": "Meta Front-End Developer", "provider": "Coursera/Meta", "cost_usd": 49, "validity_years": 1}]

    total_weeks = sum(g["time_to_proficiency_weeks"] for g in gaps)
    return {
        "total_gaps_found": len(gaps),
        "critical_gaps": gaps,
        "learning_sequence": sequence,
        "total_est_weeks": total_weeks,
        "study_plan": {"daily_hours": 1.5, "sessions_per_week": 5, "completion_in_weeks": total_weeks},
        "certification_suggestions": certs,
        "quick_win": f"Bugün '{gaps[0]['skill']}' için resmi dokumentasyonu aç ve ilk 30 sayfayı oku (30 dakika)",
        "source": "mock",
    }
