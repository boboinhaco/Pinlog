from datetime import date, datetime, time, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..db.models import CalendarEvent, SavedItem
from ..core.security import current_user
from ..core.errors import ok

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


# 기간과 겹치는 이벤트 + 항목 제목/장소
@router.get("")
async def range_events(from_: date = Query(alias="from"), to: date = Query(), user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    start = datetime.combine(from_, time.min, tzinfo=timezone.utc); end = datetime.combine(to, time.max, tzinfo=timezone.utc)
    rows = (await db.execute(select(CalendarEvent, SavedItem).join(SavedItem, SavedItem.item_id == CalendarEvent.item_id)
                             .where(SavedItem.user_id == user_id, CalendarEvent.start_at <= end, func.coalesce(CalendarEvent.end_at, CalendarEvent.start_at) >= start).order_by(CalendarEvent.start_at))).all()
    return ok([{"event_id": str(e.event_id), "item_id": str(i.item_id), "title": i.title, "category": i.category, "event_type": e.event_type,
                "start_at": e.start_at.isoformat(), "end_at": e.end_at.isoformat() if e.end_at else None, "date_status": e.date_status, "location": i.fields_json.get("location")} for e, i in rows])


# 캘린더 앱에 넣을 수 있는 .ics 파일 (종일 일정, 종료일은 ICS 규칙대로 다음날)
TYPE_LABEL = {"APPLY_START": "신청 시작", "APPLY_END": "신청 마감", "EVENT_PERIOD": "", "VISIT": "방문"}


def _ics_text(v: str) -> str:
    return v.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


@router.get("/ics")
async def export_ics(user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    from datetime import timedelta
    from fastapi import Response
    rows = (await db.execute(select(CalendarEvent, SavedItem).join(SavedItem, SavedItem.item_id == CalendarEvent.item_id)
                             .where(SavedItem.user_id == user_id, SavedItem.status == "ACTIVE").order_by(CalendarEvent.start_at))).all()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Pinlog//KR", "CALSCALE:GREGORIAN", "X-WR-CALNAME:Pinlog"]
    for e, i in rows:
        start = e.start_at.date(); end = (e.end_at or e.start_at).date() + timedelta(days=1)
        label = TYPE_LABEL.get(e.event_type, "")
        summary = f"{i.title} ({label})" if label else i.title
        loc = (i.fields_json.get("location") or {})
        lines += ["BEGIN:VEVENT", f"UID:{e.event_id}@pinlog", f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                  f"SUMMARY:{_ics_text(summary)}"]
        if loc.get("name"): lines.append(f"LOCATION:{_ics_text(' '.join(x for x in (loc.get('name'), loc.get('address')) if x))}")
        if i.fields_json.get("source_url"): lines.append(f"URL:{i.fields_json['source_url']}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return Response("\r\n".join(lines) + "\r\n", media_type="text/calendar; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="pinlog.ics"'})
