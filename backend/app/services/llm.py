import httpx
from app.config import get_settings


def get_llm_config(llm_id: str) -> tuple[str, str]:
    settings = get_settings()
    if llm_id == "llm_1":
        return settings.LLM_1_URL, settings.LLM_1_API_KEY
    if llm_id == "llm_2":
        return settings.LLM_2_URL, settings.LLM_2_API_KEY
    if llm_id == "llm_3":
        return settings.LLM_3_URL, settings.LLM_3_API_KEY
    raise ValueError(f"Unknown llm_id: {llm_id}")


async def chat_completion(
    messages: list[dict],
    llm_id: str,
) -> str:
    url, api_key = get_llm_config(llm_id)
    if not url:
        return "[Ошибка: LLM не настроен. Укажите URL в .env]"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} if api_key else {"Content-Type": "application/json"}
    payload = {"messages": messages, "model": "default", "stream": False}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url.rstrip("/") + "/v1/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        return "[Пустой ответ от модели]"
    return (choices[0].get("message") or {}).get("content") or "[Пустой ответ]"
