"""
Briefing Router – /api/v1/briefing
Günlük yapay zeka sesli brifing endpoint'leri
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from api.v1.auth_utils import get_current_user_id
from api.v1.database import get_user
from api.v1.agents.orchestrator_agent import orchestrate
from api.v1.services.tts_service import generate_briefing_text, text_to_speech_base64, get_tts_status

router = APIRouter(prefix="/briefing")


class BriefingResponse(BaseModel):
    text: str
    audio_base64: Optional[str] = None
    audio_available: bool = False
    tts_engine: str = "none"


@router.get("/daily", summary="📋 Günlük AI brifing metnini döner")
async def get_daily_briefing(user_id: str = Depends(get_current_user_id)):
    """
    Orchestrator agent analizini kullanarak kullanıcıya özel günlük brifing metni üretir.
    """
    user_data = get_user(user_id) or {}
    
    try:
        orchestrator_result = orchestrate(user_id)
    except Exception as e:
        print(f"[Briefing] Orchestrator error: {e}")
        orchestrator_result = {
            "archetype": {"name": "Dijital Kaşif"},
            "today_focus": {"primary": "Bugünün görevlerini tamamlamak"},
            "opportunities": [],
            "warnings": []
        }

    briefing_text = generate_briefing_text(user_data, orchestrator_result)

    status = get_tts_status()
    return {
        "text": briefing_text,
        "audio_available": status["active_engine"] != "none",
        "tts_engine": status["active_engine"],
        "orchestrator_summary": {
            "archetype": orchestrator_result.get("archetype", {}),
            "today_focus": orchestrator_result.get("today_focus", {}),
        }
    }


@router.post("/tts", summary="🎙️ Metni sese çevirir (MP3 base64)")
async def synthesize_speech(
    payload: dict,
    user_id: str = Depends(get_current_user_id)
):
    """
    Verilen metni gTTS veya Google Cloud TTS ile MP3'e çevirir.
    Response'da base64 encoded MP3 döner; frontend <audio> ile çalar.
    """
    text = payload.get("text", "")
    lang = payload.get("lang", "tr")

    if not text:
        return {"audio_base64": None, "error": "Metin boş olamaz."}

    # Max 500 karakter ile sınırla
    text = text[:500]

    audio_b64 = text_to_speech_base64(text, lang)

    status = get_tts_status()
    return {
        "audio_base64": audio_b64,
        "audio_available": audio_b64 is not None,
        "tts_engine": status["active_engine"],
        "char_count": len(text)
    }


@router.get("/tts/status", summary="TTS motor durumu")
async def tts_status():
    """Hangi TTS motorunun aktif olduğunu döner."""
    return get_tts_status()
