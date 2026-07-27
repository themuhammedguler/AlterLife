"""Shared Groq client helpers for text/JSON and vision workloads."""

import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import httpx

GROQ_API_URL = os.getenv(
    "GROQ_API_URL",
    "https://api.groq.com/openai/v1/chat/completions",
)
DEFAULT_TEXT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_VISION_MODEL = "qwen/qwen3.6-27b"


class AIProviderUnavailable(RuntimeError):
    """Raised when Groq is not configured or cannot return a usable response."""


def is_groq_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def _chat_completion(
    messages: List[Dict[str, Any]],
    *,
    model: str,
    json_mode: bool = False,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIProviderUnavailable("GROQ_API_KEY yapılandırılmamış.")

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = httpx.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise AIProviderUnavailable(f"Groq isteği başarısız: {exc}") from exc

    if not isinstance(content, str) or not content.strip():
        raise AIProviderUnavailable("Groq boş yanıt döndürdü.")
    return content.strip()


def call_groq_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    *,
    expect_array: bool = False,
    required_keys: Sequence[str] = (),
    model: Optional[str] = None,
    retries: int = 2,
    validator: Optional[Callable[[Any], bool]] = None,
) -> Union[Dict[str, Any], List[Any]]:
    messages: List[Dict[str, Any]] = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    # Groq JSON mode requires a JSON object. Array responses are wrapped and
    # unwrapped so callers can keep their existing list-oriented contracts.
    if expect_array:
        messages[-1]["content"] += (
            '\nYanıtı yalnızca {"items": [...]} biçiminde geçerli bir JSON nesnesi olarak döndür.'
        )
    selected_model = model or os.getenv("GROQ_TEXT_MODEL", DEFAULT_TEXT_MODEL)
    # Compound systems support web tools but not every OpenAI JSON-mode option.
    json_mode = not selected_model.startswith("groq/compound")
    last_error: Optional[Exception] = None

    for attempt in range(retries + 1):
        try:
            raw = _chat_completion(messages, model=selected_model, json_mode=json_mode)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.removeprefix("```json").removeprefix("```")
                cleaned = cleaned.removesuffix("```").strip()
            data = json.loads(cleaned)
            result: Any = data
            if expect_array:
                if isinstance(data, dict) and isinstance(data.get("items"), list):
                    result = data["items"]
                else:
                    raise ValueError("Beklenen items listesi eksik.")
            elif not isinstance(data, dict):
                raise ValueError("Beklenen JSON nesnesi dönmedi.")

            if isinstance(result, dict):
                missing = [key for key in required_keys if key not in result]
                if missing:
                    raise ValueError(f"Eksik alanlar: {', '.join(missing)}")
            if validator and not validator(result):
                raise ValueError("Yanıt uygulama şemasını karşılamıyor.")
            return result
        except (json.JSONDecodeError, ValueError, AIProviderUnavailable) as exc:
            last_error = exc
            if attempt >= retries:
                break
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Önceki yanıt geçersizdi ({exc}). Açıklama veya markdown eklemeden, "
                        "istenen bütün alanlarla geçerli JSON'u yeniden döndür."
                    ),
                }
            )

    raise AIProviderUnavailable(f"Groq doğrulanabilir JSON döndüremedi: {last_error}")


def call_groq_research_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    **kwargs: Any,
) -> Union[Dict[str, Any], List[Any]]:
    """Run a current-information prompt through Groq Compound web search."""
    return call_groq_json(
        prompt,
        system_instruction,
        model=os.getenv("GROQ_RESEARCH_MODEL", "groq/compound"),
        **kwargs,
    )


def analyze_image_with_groq(photo_base64: str, prompt: str, mime_type: str = "image/jpeg") -> str:
    content = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{photo_base64}"},
        },
    ]
    return _chat_completion(
        [{"role": "user", "content": content}],
        model=os.getenv("GROQ_VISION_MODEL", DEFAULT_VISION_MODEL),
    )
