from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..db.models import SavedItem
from ..core.security import current_user
from ..core.errors import ok

router = APIRouter(prefix="/api/places", tags=["places"])


# 저장 항목의 location을 장소 목록으로 (이름 기준 중복 제거, 최신 우선)
@router.get("")
async def list_places(user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    items = (await db.execute(select(SavedItem).where(SavedItem.user_id == user_id, SavedItem.status == "ACTIVE")
                              .order_by(SavedItem.created_at.desc()))).scalars().all()
    places: dict[str, dict] = {}
    for i in items:
        loc = i.fields_json.get("location") or {}
        if not loc.get("name"): continue
        p = places.setdefault(loc["name"], {**loc, "items": []})
        p["items"].append({"item_id": str(i.item_id), "title": i.title, "event_period": i.fields_json.get("event_period")})
    return ok(list(places.values()))
