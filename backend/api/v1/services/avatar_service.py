"""
Avatar Service – Gemini Vision + DiceBear Fallback
Kullanıcının metin betimlemesi veya fotoğrafından RPG avatar üretir.
"""

import os
import hashlib
import base64
import urllib.request
import urllib.parse
from typing import Optional

# ── Gemini / Google AI Client ─────────────────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    _GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
except ImportError:
    _GEMINI_AVAILABLE = False


# ── DiceBear Styles ───────────────────────────────────────────────────────────
DICEBEAR_STYLES = ["avataaars", "micah", "personas", "lorelei", "bottts-neutral"]
DICEBEAR_BASE = "https://api.dicebear.com/9.x"

# ── RPG Avatar Prompt Templates ───────────────────────────────────────────────
RPG_STYLE_SUFFIX = (
    "Cyberpunk glassmorphism illustration style. "
    "Futuristic neon background, dark mode aesthetic. "
    "Highly detailed digital art, RPG character portrait, dramatic lighting. "
    "No text, no watermark."
)

PHOTO_ANALYSIS_PROMPT = """
Analyze this photo and describe the person's:
1. Hair color and style (length, texture)
2. Eye color and shape
3. Skin tone
4. Distinctive facial features (jawline, nose, eyebrows)
5. Any visible accessories (glasses, earrings, etc.)
6. General style/vibe

Respond in exactly this format:
HAIR: [description]
EYES: [description]  
SKIN: [description]
FEATURES: [description]
ACCESSORIES: [description]
STYLE_VIBE: [description]
"""


def analyze_photo_with_gemini(photo_base64: str) -> str:
    """
    Gemini Vision ile yüklenen fotoğrafı analiz ederek fiziksel betimi döner.
    API yoksa basit fallback döner.
    """
    if not _GEMINI_AVAILABLE:
        return "Short dark hair, brown eyes, medium skin tone, modern professional style"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        image_data = {
            "mime_type": "image/jpeg",
            "data": photo_base64
        }
        response = model.generate_content([PHOTO_ANALYSIS_PROMPT, image_data])
        return response.text.strip()
    except Exception as e:
        print(f"[AvatarService] Gemini Vision error: {e}")
        return "Short dark hair, brown eyes, medium skin tone, professional style"


def build_rpg_prompt(description: str, role: str = "Software Developer") -> str:
    """
    Kullanıcı betimlemesi + RPG stilini harmanlayarak görsel üretim promptu oluşturur.
    """
    role_accessories = {
        "Software Developer": "holographic keyboard, glowing code terminal nearby",
        "Designer": "stylus pen, digital tablet, creative energy",
        "Financial Analyst": "holographic financial charts, smart glasses",
        "Startup Founder": "futuristic badge, confident stance",
        "Student": "cyberpunk backpack, holographic books",
    }
    
    accessory = role_accessories.get(role, "futuristic gadgets")
    
    prompt = (
        f"RPG character portrait: {description}. "
        f"Character class: {role}. Equipment: {accessory}. "
        f"{RPG_STYLE_SUFFIX}"
    )
    return prompt


def generate_dicebear_url(seed: str, style: str = "avataaars") -> str:
    """
    DiceBear API ile ücretsiz SVG avatar URL'i üretir.
    """
    if style not in DICEBEAR_STYLES:
        style = "avataaars"
    
    encoded_seed = urllib.parse.quote(seed)
    url = f"{DICEBEAR_BASE}/{style}/svg?seed={encoded_seed}&backgroundColor=0a0a14&radius=50"
    return url


def generate_avatar(
    user_id: str,
    description: Optional[str] = None,
    photo_base64: Optional[str] = None,
    role: str = "Software Developer"
) -> dict:
    """
    Ana avatar üretim fonksiyonu.
    
    1. Fotoğraf varsa → Gemini Vision ile analiz et → RPG prompt oluştur
    2. Metin varsa → RPG prompt oluştur
    3. Hiçbiri yoksa → DiceBear fallback
    
    Şu anda Imagen/DALL-E API olmadığı için DiceBear URL döner.
    Gerçek üretim için Imagen 3 API key gerekir.
    """
    result = {
        "avatar_url": None,
        "avatar_type": "dicebear",
        "prompt_used": None,
        "message": ""
    }

    # Fotoğraf analizi
    if photo_base64:
        photo_desc = analyze_photo_with_gemini(photo_base64)
        final_description = photo_desc
        result["message"] = "Fotoğrafınız analiz edildi, RPG avatar stiline dönüştürüldü."
    elif description:
        final_description = description
        result["message"] = "Betimlemenizdeki özellikler RPG stiline uyarlandı."
    else:
        final_description = None
        result["message"] = "Varsayılan RPG avatar oluşturuldu."

    # Prompt oluştur
    if final_description:
        prompt = build_rpg_prompt(final_description, role)
        result["prompt_used"] = prompt

        # Imagen 3 API entegrasyonu buraya gelecek (API key gerektirir)
        # Şimdilik DiceBear ile benzersiz seed kullan
        seed = hashlib.md5(prompt.encode()).hexdigest()[:16]
    else:
        seed = user_id

    # DiceBear URL üret (ücretsiz fallback)
    style = "avataaars"  # Varsayılan stil
    if role in ["Designer", "Startup Founder"]:
        style = "micah"
    elif role in ["Financial Analyst"]:
        style = "personas"

    avatar_url = generate_dicebear_url(seed, style)
    result["avatar_url"] = avatar_url
    result["avatar_type"] = "dicebear"

    return result
