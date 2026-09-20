import asyncio, base64, json
import httpx
from ..core.config import settings

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
RETRY_STATUS = (429, 500, 503)
MSG_DAILY = "오늘 쓸 수 있는 AI 무료 사용량을 다 썼어요. 내일 다시 시도하거나, Google AI Studio에서 결제를 켜면 바로 이어서 쓸 수 있어요."
MSG_BURST = "AI 요청이 잠시 몰렸어요. 1분 뒤 다시 시도해 주세요."
MSG_BUSY = "AI 서버가 잠시 붐벼요. 잠시 후 다시 시도해 주세요."


class LLMError(Exception):
    pass


last_model: str | None = None   # 마지막으로 성공한 모델 (대체 모델이 답했는지 기록용)


# 429 응답에서 (일일 한도인지, 권장 대기 초) 읽기
def _quota_info(res: httpx.Response) -> tuple[bool, float | None]:
    try:
        details = res.json().get("error", {}).get("details", [])
    except ValueError:
        return False, None
    daily, delay = False, None
    for d in details:
        t = d.get("@type", "")
        if t.endswith("QuotaFailure"):
            daily = daily or any("PerDay" in v.get("quotaId", "") for v in d.get("violations", []))
        elif t.endswith("RetryInfo") and str(d.get("retryDelay", "")).endswith("s"):
            try: delay = float(d["retryDelay"][:-1])
            except ValueError: pass
    return daily, delay


def _models() -> list[str]:
    extra = [m.strip() for m in settings.llm_fallback_models.split(",") if m.strip()]
    return [settings.llm_model] + [m for m in extra if m != settings.llm_model]


# Gemini JSON 응답 호출, 이미지는 (mime, bytes) 목록으로 첨부
# 무료 등급 일일 한도(429 PerDay)나 없어진 모델(404)은 즉시 다음 모델로, 일시 과부하(5xx)나 분당 한도는 잠깐 기다렸다 한 번 더
async def generate_json(prompt: str, images: list[tuple[str, bytes]] | None = None, timeout: float = 45) -> dict:
    if not settings.llm_api_key: raise LLMError("LLM_API_KEY가 설정되지 않았어요.")
    parts = [{"text": prompt}] + [{"inline_data": {"mime_type": m, "data": base64.b64encode(b).decode()}} for m, b in images or []]
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2, "thinkingConfig": {"thinkingLevel": "low"}}}
    last, daily_hit = None, False
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model in _models():
            for attempt in range(2):
                try:
                    res = await client.post(API.format(model=model), json=body, headers={"x-goog-api-key": settings.llm_api_key})
                except httpx.TimeoutException:
                    continue
                if res.status_code == 200:
                    global last_model; last_model = model
                    return _parse(res)
                last = res
                if res.status_code == 404: break                      # 모델 없음 → 다음 모델
                if res.status_code not in RETRY_STATUS:
                    raise LLMError(f"LLM 호출 실패 ({res.status_code}): {res.text[:200]}")
                if res.status_code == 429:
                    daily, delay = _quota_info(res)
                    if daily: daily_hit = True; break                  # 오늘 한도 → 이 모델은 포기
                    if attempt == 0 and delay and delay <= 20: await asyncio.sleep(delay); continue
                    break                                             # 오래 기다려야 하면 다음 모델
                if attempt == 0: await asyncio.sleep(2)                # 500/503: 잠깐 뒤 한 번 더
    if last is not None and last.status_code == 429: raise LLMError(MSG_DAILY if daily_hit else MSG_BURST)
    raise LLMError(MSG_BUSY)


def _parse(res: httpx.Response) -> dict:
    cand = (res.json().get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"LLM 응답이 JSON이 아니에요: {text[:200]}") from e
