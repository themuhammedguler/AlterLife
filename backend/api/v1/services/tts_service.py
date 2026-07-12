"""
TTS Service – Günlük AI Brifing Metin-to-Ses Servisi
gTTS (ücretsiz) ile ses üretir. Google Cloud TTS varsa onu kullanır.
"""

import os
import io
import base64
from typing import Optional

# gTTS – pip install gtts
try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

# Google Cloud TTS (opsiyonel, premium kalite)
try:
    from google.cloud import texttospeech
    _CLOUD_TTS_AVAILABLE = bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
except ImportError:
    _CLOUD_TTS_AVAILABLE = False


def generate_briefing_text(user_data: dict, orchestrator_result: dict) -> str:
    """
    Orchestrator agent sonucundan kullanıcıya özgü günlük brifing metni üretir.
    """
    display_name = user_data.get("displayName") or user_data.get("display_name", "Kaşif")
    first_name = display_name.split()[0] if display_name else "Kaşif"
    
    # Orchestrator sonucundan veri çek
    archetype = orchestrator_result.get("archetype", {})
    today_focus = orchestrator_result.get("today_focus", {})
    opportunities = orchestrator_result.get("opportunities", [])
    warnings = orchestrator_result.get("warnings", [])
    
    archetype_name = archetype.get("name", "Dijital Kaşif")
    primary_focus = today_focus.get("primary", "Kariyer gelişimine odaklanmak")
    
    # Fırsatlar ve uyarılar (ilk 2 tane)
    opp_text = ""
    if opportunities:
        opp_items = opportunities[:2]
        opp_text = " ".join([f"{o.get('title', '')}." for o in opp_items])
    
    warn_text = ""
    if warnings:
        warn_items = warnings[:1]
        warn_text = f"Dikkat: {warn_items[0].get('message', '')}." if warn_items else ""

    text = (
        f"Günaydın {first_name}. Ben AlterLife Yapay Zekası. "
        f"Profil analizine göre senin arketipin '{archetype_name}'. "
        f"Bugünkü odak noktanı dinle: {primary_focus}. "
        f"{opp_text} "
        f"{warn_text} "
        f"Hayallerini gerçekleştirmek için bugün de bir adım at. "
        f"AlterLife seninle."
    )
    
    return text.strip()


def text_to_speech_base64(text: str, lang: str = "tr") -> Optional[str]:
    """
    Metni sese çevirir ve base64 string olarak döner.
    
    Öncelik sırası:
    1. Google Cloud TTS (premium kalite, API key gerekir)
    2. gTTS (ücretsiz, internet gerekir)
    3. None (her ikisi de yoksa)
    """
    
    # 1. Google Cloud TTS
    if _CLOUD_TTS_AVAILABLE:
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="tr-TR",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
            return audio_b64
        except Exception as e:
            print(f"[TTS] Google Cloud TTS error: {e}")

    # 2. gTTS (ücretsiz fallback)
    if _GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            mp3_buffer = io.BytesIO()
            tts.write_to_fp(mp3_buffer)
            mp3_buffer.seek(0)
            audio_b64 = base64.b64encode(mp3_buffer.read()).decode("utf-8")
            return audio_b64
        except Exception as e:
            print(f"[TTS] gTTS error: {e}")

    return None


def get_tts_status() -> dict:
    """
    Hangi TTS motorunun aktif olduğunu döner.
    """
    return {
        "google_cloud_tts": _CLOUD_TTS_AVAILABLE,
        "gtts": _GTTS_AVAILABLE,
        "active_engine": (
            "google_cloud_tts" if _CLOUD_TTS_AVAILABLE
            else "gtts" if _GTTS_AVAILABLE
            else "none"
        )
    }
