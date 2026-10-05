"""Cliente LLM único: habla con el proxy LiteLLM y devuelve JSON limpio."""
import json
import re
import time

from openai import OpenAI

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, log

_client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=120)
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_thinking(text: str) -> str:
    """Qwen3 puede devolver su razonamiento entre <think>...</think>; lo quitamos."""
    return _THINK_RE.sub("", text or "").strip()


def extract_json(text: str):
    """Extrae el primer objeto/lista JSON de una respuesta (con o sin bloque de código markdown)."""
    text = strip_thinking(text)
    text = re.sub(re.escape("`" * 3) + r"(?:json)?", "", text).strip()
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError("La respuesta no contiene JSON")
    start = min(starts)
    end = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[start : end + 1])


def chat_json(system: str, user: str, model: str | None = None, retries: int = 3):
    """Devuelve (datos_json, modelo_real_que_respondió). Reintenta con espera creciente."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = _client.chat.completions.create(
                model=model or LLM_MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.2,
                max_tokens=4000,
            )
            content = resp.choices[0].message.content or ""
            return extract_json(content), resp.model
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            wait = 2 ** attempt
            log.warning("LLM intento %d/%d falló (%s). Espero %ds", attempt, retries, str(exc)[:120], wait)
            time.sleep(wait)
    raise RuntimeError(f"El LLM falló tras {retries} intentos: {last_error}")