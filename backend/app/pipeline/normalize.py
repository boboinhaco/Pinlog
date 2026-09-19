import asyncio, re
from datetime import date
import httpx
from ..schemas import ExtractionPayload

# 금액 문자열 → 원 단위 정수
def parse_amount(text: str | None) -> int | None:
    if not text: return None
    m = re.search(r"(\d[\d,]*)\s*(만|억)?\s*원?", text)
    if not m: return None
    n = int(m.group(1).replace(",", ""))
    return n * {"만": 10_000, "억": 100_000_000}.get(m.group(2), 1)


# "9월까지" 같은 상대 표현을 후보 날짜로, 확정은 사용자 확인
def resolve_relative_end(text: str, today: date | None = None) -> tuple[str | None, str]:
    today = today or date.today()
    m = re.search(r"(\d{1,2})월\s*까지", text)
    if m:
        month = int(m.group(1)); year = today.year if month >= today.month else today.year + 1
        import calendar
        return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}", "ambiguous"
    return None, "unknown"


# 장소명/주소 → 좌표 (OSM Nominatim, 초당 1회 제한 준수), 실패하면 좌표 없이 둠
VAGUE = ("전역", "온라인", "전국", "각 지역", "곳곳", "미정")


async def geocode(name: str | None, address: str | None) -> tuple[float, float] | None:
    if not address and (not name or any(v in name for v in VAGUE)): return None
    for q in [q for q in (address, f"{name} {address or ''}".strip(), name) if q]:
        try:
            async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "NEXTO/0.3 (demo; https://github.com/boboinhaco/NEXTO_Wicked)"}) as client:
                res = await client.get("https://nominatim.openstreetmap.org/search", params={"q": q, "format": "json", "limit": 1, "countrycodes": "kr"})
            hits = res.json() if res.status_code == 200 else []
            await asyncio.sleep(1)
            if hits: return float(hits[0]["lat"]), float(hits[0]["lon"])
        except Exception:
            return None
    return None


async def _fill_coords(loc: dict | None) -> dict | None:
    if not loc or not loc.get("name") or loc.get("lat") is not None: return loc
    hit = await geocode(loc.get("name"), loc.get("address"))
    return {**loc, "lat": hit[0], "lng": hit[1]} if hit else loc


# A5: 규칙 우선 정규화 (금액 정수화, 장소 좌표)
async def run(ex: ExtractionPayload) -> ExtractionPayload:
    if ex.benefit_amount and ex.benefit_amount.get("text") and not ex.benefit_amount.get("value"):
        ex.benefit_amount["value"] = parse_amount(ex.benefit_amount["text"])
    ex.location = await _fill_coords(ex.location)
    for ev in ex.events:
        if ev.location and ev.location.lat is None:
            hit = await geocode(ev.location.name, ev.location.address)
            if hit: ev.location.lat, ev.location.lng = hit
    return ex
