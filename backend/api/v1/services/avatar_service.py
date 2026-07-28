"""
Avatar Service – Groq Vision + DiceBear Fallback
Kullanıcının metin betimlemesi veya fotoğrafından RPG avatar üretir.
"""

import base64
import hashlib
import os
import urllib.parse
from typing import Optional

import httpx

from api.v1.services.ai_service import analyze_image_with_groq, is_groq_configured


# ── DiceBear Styles ───────────────────────────────────────────────────────────
DICEBEAR_STYLES = ["avataaars", "micah", "personas", "lorelei", "bottts-neutral"]
DICEBEAR_BASE = os.getenv("DICEBEAR_API_URL", "https://api.dicebear.com/9.x")

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


def analyze_photo_with_groq(photo_base64: str, mime_type: str = "image/jpeg") -> str:
    """
    Groq Vision ile yüklenen fotoğrafı analiz ederek fiziksel betimi döner.
    API yoksa basit fallback döner.
    """
    if not is_groq_configured():
        return "Short dark hair, brown eyes, medium skin tone, modern professional style"

    try:
        return analyze_image_with_groq(photo_base64, PHOTO_ANALYSIS_PROMPT, mime_type)
    except Exception as e:
        print(f"[AvatarService] Groq Vision error: {e}")
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


def generate_ai_image(prompt: str) -> Optional[str]:
    """Optionally generate a real image; return URL/data URL or None."""
    if os.getenv("AVATAR_IMAGE_PROVIDER", "").lower() != "openai":
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        response = httpx.post(
            os.getenv("OPENAI_IMAGES_API_URL", "https://api.openai.com/v1/images/generations"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
                "prompt": prompt,
                "size": "1024x1024",
                "quality": os.getenv("OPENAI_IMAGE_QUALITY", "medium"),
                "output_format": "png",
            },
            timeout=120.0,
        )
        response.raise_for_status()
        item = response.json()["data"][0]
        if item.get("url"):
            return item["url"]
        if item.get("b64_json"):
            # The local JSON database can persist this. Production deployments
            # should upload it to Firebase Storage and save the resulting URL.
            base64.b64decode(item["b64_json"], validate=True)
            return f"data:image/png;base64,{item['b64_json']}"
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"[AvatarService] Image generation failed: {exc}")
    return None


def generate_avatar(
    user_id: str,
    description: Optional[str] = None,
    photo_base64: Optional[str] = None,
    photo_mime_type: str = "image/jpeg",
    role: str = "Software Developer"
) -> dict:
    """
    Ana avatar üretim fonksiyonu.
    
    1. Fotoğraf varsa → Groq Vision ile analiz et → RPG prompt oluştur
    2. Metin varsa → RPG prompt oluştur
    3. Hiçbiri yoksa → DiceBear fallback
    
    OpenAI Images yapılandırılmışsa özgün görsel, aksi halde DiceBear URL döner.
    """
    result = {
        "avatar_url": None,
        "avatar_type": "dicebear",
        "prompt_used": None,
        "message": ""
    }

    # Fotoğraf analizi
    if photo_base64:
        photo_desc = analyze_photo_with_groq(photo_base64, photo_mime_type)
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
        seed = hashlib.md5(prompt.encode()).hexdigest()[:16]
        generated_url = generate_ai_image(prompt)
        if generated_url:
            result["avatar_url"] = generated_url
            result["avatar_type"] = "ai_generated"
            result["message"] = "Özgün RPG avatarınız yapay zekâ ile üretildi."
            return result
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
