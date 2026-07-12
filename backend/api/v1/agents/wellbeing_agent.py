"""
WellbeingAgent – Burnout riski, stres analizi, kişiselleştirilmiş iyileşme önerileri
"""
import os, json
from typing import Dict, Any

GEMINI_SYSTEM = "Sen pozitif psikoloji ve iş-yaşam dengesi uzmanısın. Empati ile yaklaş, somut ve uygulanabilir öneriler sun. SADECE JSON döndür. Türkçe yaz."

def check_wellbeing(user_profile: Dict[str, Any], profile_analysis: Dict[str, Any]) -> Dict[str, Any]:
    stress = user_profile.get("stress_level", 40)
    happiness = user_profile.get("happiness", 65)
    active_days = user_profile.get("active_days", 5)
    level = user_profile.get("level", 1)
    xp = user_profile.get("xp", 0)
    archetype = profile_analysis.get("archetype", "Pratik")

    # Burnout score heuristic: high stress + low happiness + low active days
    burnout_score = min(100, max(0, stress * 0.5 + (100 - happiness) * 0.3 + max(0, 7 - active_days) * 3))
    risk_level = "Kritik" if burnout_score >= 70 else "Yüksek" if burnout_score >= 50 else "Orta" if burnout_score >= 30 else "Düşük"

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
                system_instruction=GEMINI_SYSTEM)
            prompt = f"""
Kullanıcı Sağlık Metrikleri:
- Stres Seviyesi: {stress}/100
- Mutluluk: {happiness}/100
- Aktif Çalışma Günü (haftalık): {active_days}
- Arketip: {archetype}
- Burnout Skoru: {burnout_score:.0f}/100
- Risk Seviyesi: {risk_level}

Bu kullanıcı için kapsamlı bir iyilik analizi yap:
- burnout_score: {burnout_score:.0f} (hesaplanmış)
- risk_level: {risk_level}
- risk_explanation: Neden bu risk seviyesinde? (Türkçe, 1-2 cümle)
- recovery_recommendations: [5 somut iyileşme önerisi, her biri {{ "action": "...", "frequency": "...", "why": "..." }}]
- energy_audit: {{ "drains": [3 enerji tüketici], "boosters": [3 enerji kaynağı] }}
- weekly_ritual: Bu kullanıcı için 7 günlük refah ritüeli öner
- motivational_message: Empati dolu, kişiye özel motivasyon mesajı
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            result["source"] = "gemini"
            return result
        except Exception as e:
            print(f"[WellbeingAgent] Gemini failed: {e}")

    # Mock fallback
    recs_by_risk = {
        "Kritik": [
            {"action": "Bu hafta 1 tam gün çalışma molası ver", "frequency": "Haftada 1", "why": "Zihinsel şarj için acil gerekli"},
            {"action": "Günde 20 dakika yürüyüş yap", "frequency": "Her gün", "why": "Kortizol düşürür, enerji verir"},
            {"action": "Ekran süresini günde 8 saatle sınırla", "frequency": "Her gün", "why": "Göz ve zihin yorgunluğunu azaltır"},
            {"action": "Haftalık 1 hobi saati ayır (müzik, spor, sanat)", "frequency": "Haftada 1", "why": "Anlam ve keyif duygusu besler"},
            {"action": "Güvendiğin biriyle 30 dakika konuş", "frequency": "Haftada 2", "why": "Duygusal boşalma kritik önemde"},
        ],
        "Yüksek": [
            {"action": "Günde en az 7 saat uy", "frequency": "Her gün", "why": "Uyku kalitesi performansın temelidir"},
            {"action": "Öğle yemeğini bilgisayar başında yeme", "frequency": "Her gün", "why": "Küçük molalar üretkenliği artırır"},
            {"action": "Haftada 3 gün 30 dakika egzersiz", "frequency": "Haftada 3", "why": "Stres hormonu sıfırlar"},
            {"action": "Gece 22:00'den sonra iş maili açma", "frequency": "Her gün", "why": "Zihinsel sınırlar sağlık için zorunlu"},
            {"action": "Bir şükran günlüğü tut, her gece 3 şey yaz", "frequency": "Her gece", "why": "Pozitif odak mutluluk hissini artırır"},
        ],
        "Orta": [
            {"action": "Pomodoro tekniği uygula (25+5 dakika)", "frequency": "Çalışma seanslarında", "why": "Odak kalitesini ve molayı dengeler"},
            {"action": "Haftada 2 kez sosyal aktivite planla", "frequency": "Haftada 2", "why": "Sosyal bağ motivasyon kaynağıdır"},
            {"action": "Sabah 10 dakika meditasyon/nefes egzersizi", "frequency": "Her gün", "why": "Gün başlangıcını sakinleştirir"},
            {"action": "Haftalık hedefleri Pazar akşamı yaz", "frequency": "Haftada 1", "why": "Netlik kaygı düşürür"},
            {"action": "Bir podcast/kitap serisi başlat (iş dışı)", "frequency": "Haftada 2-3", "why": "Zihinsel çeşitlilik önemli"},
        ],
        "Düşük": [
            {"action": "Mevcut rutinini korumaya devam et", "frequency": "Her gün", "why": "Dengen iyi, koruma mod"},
            {"action": "Yeni bir hobi veya öğrenme alanı dene", "frequency": "Haftada 1", "why": "Zihinsel büyüme için alan var"},
            {"action": "Başarılarını kutla, kendinle gurur duy", "frequency": "Her başarıda", "why": "Motivasyonu besler"},
            {"action": "Mentörlük ver veya al", "frequency": "Aylık", "why": "Deneyim paylaşımı anlam katar"},
            {"action": "Doğada zaman geçir, şehirden çık", "frequency": "Ayda 1", "why": "Perspektif sıfırlar"},
        ],
    }

    return {
        "burnout_score": round(burnout_score),
        "risk_level": risk_level,
        "risk_explanation": {
            "Kritik": f"Stres ({stress}/100) ve düşük mutluluk ({happiness}/100) kombinasyonu ciddi tükenmişlik riski yaratıyor. Acil önlem gerekli.",
            "Yüksek": f"Yüksek stres ve azalan mutluluk erken uyarı veriyor. Önleyici adımlar at.",
            "Orta": f"Dengede görünüyorsun ama stres birikimi var. Küçük iyileştirmelerle güçlü tutabilirsin.",
            "Düşük": f"Harika bir dengedesin! Rutinini koruyarak büyümeye devam et.",
        }[risk_level],
        "recovery_recommendations": recs_by_risk[risk_level],
        "energy_audit": {
            "drains": ["Uzun toplantılar", "Belirsiz hedefler", "Dikkat dağıtıcılar"],
            "boosters": ["Küçük başarı anları", "Arkadaşlarla zaman", "Fiziksel hareket"],
        },
        "weekly_ritual": f"Pzt-Cum: Pomodoro çalışma + gece günlük. Cumartesi: Dijital detoks yarım gün. Pazar: Haftaya hazırlık + şükran yazımı.",
        "motivational_message": {
            "Kritik": "Dur ve nefes al. Yorgunluk başarısızlık değil, senin bir insan olduğunun kanıtı. Önce kendine bak.",
            "Yüksek": "Uyarı sinyalleri vücudunun sana konuşma şekli. Bugün küçük bir mola ver — yarın daha güçlü dönersin.",
            "Orta": "İyi gidiyorsun! Ufak ayarlamalarla harika bir dengeye ulaşabilirsin.",
            "Düşük": "Muazzam bir dengede ilerliyorsun. Bu enerjiyi sürdür ve etrafına da ilham ver!",
        }[risk_level],
        "source": "mock",
    }
