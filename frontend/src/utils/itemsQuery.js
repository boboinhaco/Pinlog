import { periodLabel, ymd } from './events'

// 오늘 기준 D-day (0 → 오늘, 음수 → 지남)
export const daysUntil = d => Math.round((new Date(d + 'T00:00') - new Date(ymd(new Date()) + 'T00:00')) / 86400000)
export const ddayLabel = d => { const n = daysUntil(d); return n === 0 ? 'D-DAY' : n > 0 ? `D-${n}` : `D+${-n}` }

// 7일 안에 시작하거나 마감되는 항목 (알림용)
export function upcomingOf(items, days = 7) {
  const today = ymd(new Date()), until = ymd(new Date(Date.now() + days * 86400000))
  return items.flatMap(i => {
    if (i.start && i.start >= today && i.start <= until) return [{ ...i, label: `${ddayLabel(i.start)} 시작 · ${periodLabel(i.start, i.end)}`, key: i.start }]
    if (i.end && i.end >= today && i.end <= until) return [{ ...i, label: `${ddayLabel(i.end)} 마감 · ${periodLabel(i.start, i.end)}`, key: i.end }]
    return []
  }).sort((a, b) => a.key.localeCompare(b.key))
}

// 제목·장소·상품 이름으로 검색, 비어 있으면 최근 항목
export const searchItems = (items, q, limit = 8) => {
  const k = q.trim().toLowerCase()
  const text = i => [i.title, i.place?.name, ...(i.products ?? []).flatMap(p => [p.matched_name, p.name, p.brand])].filter(Boolean).join(' ').toLowerCase()
  return (k ? items.filter(i => text(i).includes(k)) : items).slice(0, limit)
}

// 아직 끝나지 않은 일정, 시작일 순
export const activeSorted = items => {
  const today = ymd(new Date())
  return items.filter(i => i.start && (i.end || i.start) >= today).sort((a, b) => a.start.localeCompare(b.start))
}
