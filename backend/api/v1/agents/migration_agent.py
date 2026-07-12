"""
MigrationAgent – Yurt dışı taşınma planlaması (Almanya, Hollanda, Kanada, ABD, İngiltere)
"""
import os, json
from typing import Dict, Any

GEMINI_SYSTEM = "Sen göç ve uluslararası kariyer danışmanısın. Vize, yaşam maliyeti, dil gereksinimleri konusunda doğru ve güncel bilgi ver. SADECE JSON döndür. Türkçe yaz."

COUNTRY_DATA = {
    "almanya": {
        "country": "Almanya", "flag": "🇩🇪",
        "visa_types": ["Mavi Kart (Nitelikli İşgücü)", "Çalışma Vizesi", "Dil Kursu + İş Arama"],
        "language_req": "B1 Almanca (Mavi Kart için İngilizce yeterli olabilir)",
        "monthly_cost_usd": {"berlin": 1800, "munich": 2200, "hamburg": 1900},
        "avg_tech_salary_usd": 70000,
        "processing_time_months": 3,
        "checklist": [
            "İş sözleşmesi veya iş teklifi mektubu al",
            "Denklik belgesi için APS/anabin.de kontrolü yap",
            "Almanca B1 sertifikası (Goethe Institut veya TELC)",
            "Blocked Account: 11.208 € yatır (öğrenci vizesi için)",
            "Sağlık sigortası düzenle (TK, DAK, Barmer)",
            "Parmak izi için Alman Büyükelçiliği randevusu al",
            "Apostil onaylı diploma, transkript, özgeçmiş hazırla",
            "Berlin / Münih'te şehir tescili için Anmeldung yap",
        ],
        "cities": [
            {"name": "Berlin", "vibe": "Startup + Yaratıcı", "cost": "1800$/ay", "english_friendly": True},
            {"name": "Münih", "vibe": "Kurumsal + Lüks", "cost": "2200$/ay", "english_friendly": True},
            {"name": "Hamburg", "vibe": "Uluslararası + Liman", "cost": "1900$/ay", "english_friendly": True},
        ],
    },
    "hollanda": {
        "country": "Hollanda", "flag": "🇳🇱",
        "visa_types": ["Nitelikli Göçmen Vizesi (HSMP)", "Çalışma İzni"],
        "language_req": "İngilizce yeterli (Hollandaca bonus)",
        "monthly_cost_usd": {"amsterdam": 2500, "eindhoven": 1800, "rotterdam": 2000},
        "avg_tech_salary_usd": 65000,
        "processing_time_months": 2,
        "checklist": [
            "Nitelikli göçmen olarak şirket sponsorluğu al",
            "Apostil onaylı diploma ve transkript",
            "BSN (Sosyal güvenlik numarası) için DigiD başvurusu",
            "30% ruling vergisi avantajı için başvur",
            "MVV vizesi için Hollanda Büyükelçiliğine başvur",
        ],
        "cities": [
            {"name": "Amsterdam", "vibe": "Fintech + Startup", "cost": "2500$/ay", "english_friendly": True},
            {"name": "Eindhoven", "vibe": "Tech + Sakin", "cost": "1800$/ay", "english_friendly": True},
        ],
    },
    "kanada": {
        "country": "Kanada", "flag": "🇨🇦",
        "visa_types": ["Express Entry (FSW)", "Provincial Nominee Program", "Work Permit"],
        "language_req": "IELTS 7.0+ veya CELPIP",
        "monthly_cost_usd": {"toronto": 2800, "vancouver": 3000, "calgary": 2200},
        "avg_tech_salary_usd": 80000,
        "processing_time_months": 6,
        "checklist": [
            "IELTS sınavına gir, 7.0+ al",
            "Express Entry profili oluştur (CRS puanı hesapla)",
            "Eğitim Credential Assessment (WES) yaptır",
            "Provincial Nominee Program araştır (Ontario, BC, Alberta)",
            "ITA (Invitation to Apply) bekle",
            "Medical exam + police clearance belgesi al",
            "LMIA veya Job Offer varsa ek puan al",
        ],
        "cities": [
            {"name": "Toronto", "vibe": "Fintech + Çeşitli", "cost": "2800$/ay", "english_friendly": True},
            {"name": "Vancouver", "vibe": "Doğa + Tech", "cost": "3000$/ay", "english_friendly": True},
            {"name": "Calgary", "vibe": "Daha uygun + Büyüyen", "cost": "2200$/ay", "english_friendly": True},
        ],
    },
}

def _detect_target_country(goal: str) -> str:
    goal_lower = goal.lower()
    if any(k in goal_lower for k in ["almanya", "berlin", "münih", "germany"]): return "almanya"
    if any(k in goal_lower for k in ["hollanda", "amsterdam", "netherlands"]): return "hollanda"
    if any(k in goal_lower for k in ["kanada", "toronto", "canada"]): return "kanada"
    return "almanya"  # Default

def create_migration_plan(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any]) -> Dict[str, Any]:
    goal = user_profile.get("freeGoal", "")
    country_key = _detect_target_country(goal)
    country = COUNTRY_DATA.get(country_key, COUNTRY_DATA["almanya"])
    monthly_savings = user_profile.get("monthly_savings", 500)
    city = country["cities"][0]

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM)
            prompt = f"""
Göç Planı İsteği:
- Hedef Ülke: {country['country']}
- Kullanıcı Hedefi: {goal}
- Aylık Birikim: {monthly_savings} USD
- Risk Toleransı: {profile_analysis.get('risk_tolerance', 'medium')}
- Arketip: {profile_analysis.get('archetype', '?')}
- Şehir: {user_profile.get('city', '?')} → {city['name']}

Kapsamlı göç planı oluştur:
- target_country: Hedef ülke adı
- recommended_city: En uygun şehir ve gerekçesi
- visa_recommendation: Hangi vize türü ve neden
- language_requirement: Dil gereksinimi ve önerilen sertifika
- financial_estimate: {{ "startup_cost_usd": ..., "monthly_living_usd": ..., "months_to_save": ... }}
- timeline: [{{ "month_range": "1-3", "actions": [...] }}, {{ "month_range": "4-6", "actions": [...] }}, ...]
- checklist: Sıralı yapılacaklar listesi (10-15 madde)
- city_comparison: [{{ "city": "...", "pro": "...", "con": "...", "cost": "..." }}]
- risk_factors: [Göç sürecindeki en büyük 3 risk]
- success_tips: [Bu ülkede yerleşimi kolaylaştıran 3 ipucu]
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[MigrationAgent] Gemini failed: {e}")

    # Mock fallback
    monthly_living = city["cost"].replace("$/ay", "").replace("$", "")
    monthly_living_int = int(monthly_living.replace(",", ""))
    startup_cost = monthly_living_int * 3 + 5000
    months_to_save = max(6, startup_cost // max(1, monthly_savings))

    return {
        "target_country": country["country"],
        "recommended_city": f"{city['name']} — {city['vibe']} ortamı, tam zamanlı İngilizce ile çalışılabilir",
        "visa_recommendation": country["visa_types"][0],
        "language_requirement": country["language_req"],
        "financial_estimate": {
            "startup_cost_usd": startup_cost,
            "monthly_living_usd": monthly_living_int,
            "months_to_save": months_to_save,
        },
        "timeline": [
            {"month_range": "1-3", "actions": ["Dil sertifikasına hazırlan", "CV'ni uluslararası formata çevir", "LinkedIn profilini güncelle"]},
            {"month_range": "4-6", "actions": ["Hedef şirkete başvurular yap", "Vize dosyasını hazırla", "Birikim hedefine ulaş"]},
            {"month_range": "7-9", "actions": ["Vize başvurusu yap", "İş teklifini onaylla", "Konut araştır"]},
            {"month_range": "10-12", "actions": ["Taşın!", "Şehir tescili yap", "Yerel ağını oluşturmaya başla"]},
        ],
        "checklist": country["checklist"],
        "city_comparison": [{"city": c["name"], "pro": c["vibe"], "con": "Kira yüksek olabilir", "cost": c["cost"]} for c in country["cities"]],
        "risk_factors": ["Kültür şoku ilk 3 ayda yoğun olabilir", "Vize gecikmesi planını bozabilir", "İlk iş teklifinin şartları beklenenden farklı çıkabilir"],
        "success_tips": ["Yerel Türk diaspora topluluğuna katıl", "İlk ay her şeyi keşfet, hemen eve kapanma", f"{city['name']}'da expat Facebook gruplarına katıl"],
        "source": "mock",
    }
