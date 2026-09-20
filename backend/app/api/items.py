from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..db.models import SavedItem, CalendarEvent, SourceDocument, VerificationResult
from ..core.security import current_user
from ..core.errors import NextoError, ok
from ..schemas import UpdateItemRequest, ManualItemRequest
from ..pipeline.normalize import geocode

router = APIRouter(prefix="/api/items", tags=["items"])


def _view(item: SavedItem):
    return {"item_id": str(item.item_id), "title": item.title, "category": item.category, "status": item.status, "fields": item.fields_json,
            "user_overrides": item.user_overrides or [], "overall_grade": item.overall_grade,
            "last_verified_at": item.last_verified_at.isoformat() if item.last_verified_at else None, "created_at": item.created_at.isoformat()}


# 검증 결과 표시용 (이전 형식: 필드 목록만 저장된 list)
def ver_view(ver: VerificationResult | None) -> dict | None:
    if not ver: return None
    data = ver.fields_json if isinstance(ver.fields_json, dict) else {"fields": ver.fields_json}
    return {**data, "overall_grade": ver.overall_grade, "verified_at": ver.verified_at.isoformat()}


def _day(v: str) -> datetime:
    return datetime.fromisoformat(v).replace(tzinfo=timezone.utc)


# fields의 apply_period로 시작/마감 이벤트, event_period로 기간 이벤트 생성
def _events(item: SavedItem) -> list[CalendarEvent]:
    period = item.fields_json.get("apply_period") or {}
    status = "AMBIGUOUS" if period.get("status") == "ambiguous" else "EXACT"
    evs = []
    if period.get("start"): evs.append(CalendarEvent(item_id=item.item_id, event_type="APPLY_START", start_at=_day(period["start"]), date_status=status))
    if period.get("end"): evs.append(CalendarEvent(item_id=item.item_id, event_type="APPLY_END", start_at=_day(period["end"]), date_status=status))
    ep = item.fields_json.get("event_period") or {}
    if ep.get("start"):
        evs.append(CalendarEvent(item_id=item.item_id, event_type="EVENT_PERIOD", start_at=_day(ep["start"]), end_at=_day(ep.get("end") or ep["start"]),
                                 date_status="AMBIGUOUS" if ep.get("status") == "ambiguous" else "EXACT"))
    return evs


# 링크 없이 직접 추가 (내 일정 > 새 일정 추가)
@router.post("/manual")
async def create_manual(req: ManualItemRequest, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if not req.title.strip(): raise NextoError("INVALID_TITLE", "일정 이름을 적어 주세요.")
    fields = {**req.fields, "location": await _located(req.fields.get("location")), "manual": True}
    item = SavedItem(user_id=user_id, title=req.title.strip()[:200], category=req.category, fields_json=fields, user_overrides=[], overall_grade="UNVERIFIED")
    db.add(item); await db.flush()
    for ev in _events(item): db.add(ev)
    await db.commit()
    return ok(_view(item))


@router.get("")
async def list_items(status: str | None = None, category: str | None = None, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = select(SavedItem).where(SavedItem.user_id == user_id).order_by(SavedItem.created_at.desc())
    if status: q = q.where(SavedItem.status == status)
    if category: q = q.where(SavedItem.category == category)
    return ok([_view(i) for i in (await db.execute(q)).scalars().all()])


# 본인 항목만 접근
async def _own(db: AsyncSession, item_id: str, user_id: str) -> SavedItem:
    item = await db.get(SavedItem, item_id)
    if not item or str(item.user_id) != str(user_id): raise NextoError("NOT_FOUND", "항목을 찾을 수 없어요.", status=404)
    return item


# FR-08: 상세 + 출처 + 근거
@router.get("/{item_id}")
async def get_item(item_id: str, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    item = await _own(db, item_id, user_id)
    src = await db.get(SourceDocument, item.primary_source_id) if item.primary_source_id else None
    ver = (await db.execute(select(VerificationResult).where(VerificationResult.extraction_id == item.extraction_id))).scalars().first() if item.extraction_id else None
    events = (await db.execute(select(CalendarEvent).where(CalendarEvent.item_id == item.item_id))).scalars().all()
    return ok({**_view(item), "source": {"url": src.url, "domain_type": src.domain_type, "title": src.title, "excerpt": src.excerpt} if src else None,
               "verification_fields": (ver_view(ver) or {}).get("fields", []), "official_summary": (ver_view(ver) or {}).get("official_summary"), "events": [{"event_type": e.event_type, "start_at": e.start_at.isoformat(), "end_at": e.end_at.isoformat() if e.end_at else None, "date_status": e.date_status} for e in events]})


# 제목·카테고리·필드 수정 (카테고리 이동)
@router.patch("/{item_id}")
async def update_item(item_id: str, req: UpdateItemRequest, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    item = await _own(db, item_id, user_id)
    if req.title: item.title = req.title
    if req.category: item.category = req.category
    if req.fields:
        item.fields_json = {**item.fields_json, **req.fields, "location": await _located(req.fields["location"]) if "location" in req.fields else item.fields_json.get("location")}
        # 날짜가 바뀌면 캘린더 이벤트 다시 만들기
        if {"apply_period", "event_period"} & req.fields.keys():
            for ev in (await db.execute(select(CalendarEvent).where(CalendarEvent.item_id == item.item_id))).scalars().all(): await db.delete(ev)
            for ev in _events(item): db.add(ev)
    if req.status: item.status = req.status
    await db.commit()
    return ok(_view(item))


# 장소명·주소만 있으면 좌표 채우기 (지도 표시용)
async def _located(loc: dict | None) -> dict | None:
    if not loc or not loc.get("name") or loc.get("lat") is not None: return loc
    hit = await geocode(loc.get("name"), loc.get("address"))
    return {**loc, "lat": hit[0], "lng": hit[1]} if hit else loc


# 삭제 (캘린더 이벤트는 FK cascade)
@router.delete("/{item_id}")
async def delete_item(item_id: str, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    item = await _own(db, item_id, user_id)
    await db.delete(item); await db.commit()
    return ok({"item_id": item_id, "deleted": True})
