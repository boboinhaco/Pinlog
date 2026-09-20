export const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const md = s => { const [, m, d] = s.split('-'); return `${+m}.${+d}` }

// "9.12 - 9.14" / 하루면 "9.18"
export const periodLabel = (start, end) => !start ? '날짜 미정' : (!end || end === start ? md(start) : `${md(start)} - ${md(end)}`)
export const longDate = s => { if (!s) return '-'; const [y, m, d] = s.split('-'); return `${y}년 ${+m}월 ${+d}일` }

// 저장 항목 → 화면용 일정 {id, title, start, end, place}
export const fromItem = i => ({
  id: i.item_id, title: i.title, category: i.category,
  start: i.fields.event_period?.start ?? i.fields.apply_period?.start ?? null,
  end: i.fields.event_period?.end ?? i.fields.apply_period?.end ?? null,
  place: i.fields.location ?? null, image: i.fields.image_url ?? null, grade: i.overall_grade,
  liked: !!i.fields.liked, created: i.created_at, summary: i.fields.summary ?? null, sourceUrl: i.fields.source_url ?? null,
  keyPoints: i.fields.key_points ?? [], officialSummary: i.fields.official_summary ?? null,
  periodKey: i.fields.event_period ? 'event_period' : i.fields.apply_period ? 'apply_period' : 'event_period'
})

// 캘린더 API 행 → 화면용 일정
export const fromCalendar = e => ({
  id: e.item_id, title: e.title, category: e.category, start: e.start_at.slice(0, 10), end: (e.end_at ?? e.start_at).slice(0, 10), place: e.location, type: e.event_type
})

// 같은 항목의 여러 이벤트(신청 시작/마감 등)를 하나의 기간으로 합침
export const mergeById = list => Object.values(list.reduce((acc, e) => {
  const cur = acc[e.id]
  acc[e.id] = !cur ? { ...e } : { ...cur, start: e.start < cur.start ? e.start : cur.start, end: e.end > cur.end ? e.end : cur.end }
  return acc
}, {})).sort((a, b) => a.start.localeCompare(b.start))

// 해당 월 1일~말일 조회 범위
export const monthRange = d => [ymd(new Date(d.getFullYear(), d.getMonth(), 1)), ymd(new Date(d.getFullYear(), d.getMonth() + 1, 0))]

// "2026. 9. 20 (토) – 10. 26 (일)" 형식
const W = ['일', '월', '화', '수', '목', '금', '토']
const full = s => { const d = new Date(s + 'T00:00'); return `${d.getMonth() + 1}. ${d.getDate()} (${W[d.getDay()]})` }
export const periodLong = (start, end) => {
  if (!start && !end) return '날짜 미정'
  const y = (start || end).slice(0, 4)
  if (!start || !end || start === end) return `${y}. ${full(start || end)}`
  return `${y}. ${full(start)} – ${full(end)}`
}

// "09.12 (토)" 형식
export const mdw = s => { const d = new Date(s + 'T00:00'); return `${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} (${W[d.getDay()]})` }
