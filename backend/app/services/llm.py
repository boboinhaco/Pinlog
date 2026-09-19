import asyncio, base64, json
import httpx
from ..core.config import settings

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
FALLBACK_MODEL = "gemini-flash-latest"
RETRY_STATUS = (429, 500, 503)


class LLMError(Exception):
    pass


# Gemini JSON 응답 호출, 이미지는 (mime, bytes) 목록으로 첨부
async def generate_json(prompt: str, images: list[tuple[str, bytes]] | None = None, timeout: float = 45) -> dict:
    if not settings.llm_api_key: raise LLMError("LLM_API_KEY가 설정되지 않았어요.")
    parts = [{"text": prompt}] + [{"inline_data": {"mime_type": m, "data": base64.b64encode(b).decode()}} for m, b in images or []]
    res = None
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2, "thinkingConfig": {"thinkingLevel": "low"}}}
    # 일시적 과부하(429/5xx)는 백오프 재시도, 마지막엔 대체 모델로
    plan = [(settings.llm_model, 0), (settings.llm_model, 2), (FALLBACK_MODEL, 4)]
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model, wait in plan:
            await asyncio.sleep(wait)
            try:
                res = await client.post(API.format(model=model), json=body, headers={"x-goog-api-key": settings.llm_api_key})
            except httpx.TimeoutException:
                continue
            if res.status_code not in RETRY_STATUS: break
    if res is None or res.status_code != 200:
        if res is not None and res.status_code in RETRY_STATUS: raise LLMError("AI 서버가 잠시 붐벼요. 잠시 후 다시 시도해 주세요.")
        raise LLMError(f"LLM 호출 실패 ({getattr(res, 'status_code', 'timeout')}): {getattr(res, 'text', '')[:200]}")
    cand = (res.json().get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"LLM 응답이 JSON이 아니에요: {text[:200]}") from e
