"""
FinancialAdvisorAgent – Birikim planı, özgürlük tarihi, yatırım önerileri
"""
import os, json
from typing import Dict, Any

GEMINI_SYSTEM = "Sen Türkiye'deki kişiler için kişisel finans danışmanısın. Pratik, gerçekçi ve kişiye özel tavsiyeler ver. SADECE JSON döndür."

def analyze_finances(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any]) -> Dict[str, Any]:
    monthly_savings = user_profile.get("monthly_savings", 500)
    risk = profile_analysis.get("risk_tolerance", "medium")
    goal = user_profile.get("freeGoal", "kariyer hedefi")
    level = user_profile.get("level", 1)
    stress = user_profile.get("stress_level", 40)

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
- Aylık Birikim: {monthly_savings} USD
- Risk Toleransı: {risk}
- Ana Hedef: {goal}
- Şu Anki Seviye/XP: {level}
- Stres Seviyesi: {stress}/100

Bu kullanıcı için kapsamlı bir finansal plan oluştur:
1. emergency_fund_months: Kaç aylık acil fon var veya olmalı? (integer)
2. monthly_plan: [ {{ "category": "kategori", "current_spend_pct": 30, "recommended_pct": 25, "action": "ne yapmalı" }} ] – En az 5 kategori
3. target_savings_usd: Hedefe ulaşmak için gereken toplam birikim
4. months_to_goal: Şu anki hızla kaç ay sürer? (integer)
5. accelerated_months: Optimize birikim ile kaç ay? (integer)
6. investment_split: {{ "gold_pct": 20, "stock_pct": 40, "crypto_pct": 10, "cash_pct": 30 }}
7. freedom_date_estimate: Tahmini finansal özgürlük yılı (YYYY formatında)
8. key_warnings: [risk faktörleri listesi, max 3]
9. quick_wins: [bu ay yapılabilecek finansal adımlar, 3 öneri]

Gerçekçi ve Türkiye ekonomisine uygun rakamlar kullan.
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[FinancialAgent] Gemini failed: {e}")

    # Mock fallback
    months_to_goal = max(6, 10000 // max(1, monthly_savings))
    accelerated = max(4, months_to_goal - int(months_to_goal * 0.25))
    from datetime import date
    freedom_year = date.today().year + (months_to_goal // 12) + 3
    investment = {"gold_pct": 30, "stock_pct": 30, "crypto_pct": 5, "cash_pct": 35} if risk == "low" else \
                 {"gold_pct": 20, "stock_pct": 45, "crypto_pct": 15, "cash_pct": 20} if risk == "high" else \
                 {"gold_pct": 25, "stock_pct": 40, "crypto_pct": 10, "cash_pct": 25}
    return {
        "emergency_fund_months": 3 if monthly_savings < 500 else 6,
        "monthly_plan": [
            {"category": "Kira / Konut", "current_spend_pct": 40, "recommended_pct": 35, "action": "Ev arkadaşı bul veya daha ucuz bölgeye taşın"},
            {"category": "Yemek", "current_spend_pct": 20, "recommended_pct": 15, "action": "Haftalık yemek planla, dışarı yeme sıklığını azalt"},
            {"category": "Ulaşım", "current_spend_pct": 10, "recommended_pct": 8, "action": "Toplu taşıma veya bisiklet"},
            {"category": "Eğlence / Abonelik", "current_spend_pct": 8, "recommended_pct": 5, "action": "Kullanılmayan abonelikleri iptal et"},
            {"category": "Birikim / Yatırım", "current_spend_pct": 15, "recommended_pct": 25, "action": "Önce acil fonu tamamla, sonra yatırım hesabı aç"},
            {"category": "Eğitim / Kurs", "current_spend_pct": 5, "recommended_pct": 8, "action": "Kariyer hedefin için sertifika yatırımı yap"},
        ],
        "target_savings_usd": months_to_goal * monthly_savings,
        "months_to_goal": months_to_goal,
        "accelerated_months": accelerated,
        "investment_split": investment,
        "freedom_date_estimate": str(freedom_year),
        "key_warnings": [
            f"Aylık {monthly_savings}$ birikimle acil fon oluşturman {3 if monthly_savings > 800 else 6} ay sürebilir",
            "Enflasyon etkisini hesaba katmadan plan yapma",
            "Tüm birikimi tek bir yatırım aracına koyma",
        ],
        "quick_wins": [
            "Bu hafta tüm aboneliklerini gözden geçir, en az 1 iptal et",
            f"Maaşının %{min(30, max(10, int(monthly_savings*100/2000)))}ini otomatik tasarruf hesabına aktar",
            "Ayda 1 'harcama izleme' günü belirle ve tüm harcamalarını kategorize et",
        ],
        "source": "mock",
    }
