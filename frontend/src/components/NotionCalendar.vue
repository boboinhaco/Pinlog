<template>
  <div class="ncal" :class="{ compact }">
    <!-- compact: 홈 카드용 (일정표 제목 + 버튼, 가로 스크롤 없이 7칸) -->
    <div v-if="compact" class="board-bar">
      <h2 class="section-title">
        <CalendarDays :size="24" />일정표 <span class="ym">{{ month.getFullYear() }}년 {{ month.getMonth() + 1 }}월</span>
      </h2>
      <div class="board-ctrl">
        <button class="ghost sq" aria-label="이전 달" @click="shift(-1)"><ChevronLeft :size="18" /></button>
        <button class="ghost sq" aria-label="다음 달" @click="shift(1)"><ChevronRight :size="18" /></button>
        <button class="ghost" @click="emit('update:month', startOfMonth(new Date()))">오늘</button>
      </div>
    </div>
    <div v-else class="bar">
      <strong>{{ month.getFullYear() }}년 {{ month.getMonth() + 1 }}월</strong>
      <div class="ctrl">
        <button class="ghost sq" aria-label="이전 달" @click="shift(-1)"><ChevronLeft :size="18" /></button>
        <button class="ghost" @click="emit('update:month', startOfMonth(new Date()))">오늘</button>
        <button class="ghost sq" aria-label="다음 달" @click="shift(1)"><ChevronRight :size="18" /></button>
      </div>
    </div>
    <div class="scroll">
      <div class="head"><span v-for="w in WEEK" :key="w">{{ w }}</span></div>
      <div v-for="(w, wi) in weeks" :key="wi" class="week" :style="{ gridTemplateRows: `28px repeat(${Math.max(w.lanes, 1)}, 24px) ${w.more.some(Boolean) ? '20px' : ''} 1fr` }">
        <div v-for="(d, di) in w.days" :key="d.key" class="day" :class="{ out: !d.inMonth, weekend: di === 0 || di === 6 }" :style="{ gridColumn: di + 1 }">
          <span class="num" :class="{ today: d.today }">{{ d.date.getDate() === 1 && !compact ? `${d.date.getMonth() + 1}월 1` : d.date.getDate() }}</span>
        </div>
        <component :is="linkable ? RouterLink : 'span'" v-for="s in w.segs" :key="s.id + s.from" :to="linkable ? `/items/${s.id}` : undefined" class="ev"
                    :class="[`tone-${s.tone}`, { cont: s.cont, open: s.open }]" :style="{ gridColumn: `${s.from + 1} / ${s.to + 2}`, gridRow: s.lane + 2 }" :title="`${s.title} (${periodLabel(s.start, s.end)})`">
          {{ s.title }}
        </component>
        <span v-for="(m, di) in w.more" v-show="m" :key="'m' + di" class="more" :style="{ gridColumn: di + 1, gridRow: w.lanes + 2 }">+{{ m }}개</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { ymd, periodLabel } from '../utils/events'
import { CATEGORY } from '../utils/labels'

// events: [{id, title, start, end, category}] (YYYY-MM-DD)
const props = defineProps({ events: { type: Array, default: () => [] }, month: { type: Date, required: true }, maxLanes: { type: Number, default: 3 }, linkable: { type: Boolean, default: true }, compact: Boolean })
const emit = defineEmits(['update:month'])
const WEEK = ['일', '월', '화', '수', '목', '금', '토']
const startOfMonth = d => new Date(d.getFullYear(), d.getMonth(), 1)
const shift = n => emit('update:month', new Date(props.month.getFullYear(), props.month.getMonth() + n, 1))

// 주 단위로 기간 이벤트를 막대(segment)로 나누고 겹치지 않게 줄(lane) 배치
const weeks = computed(() => {
  const y = props.month.getFullYear(), m = props.month.getMonth(), first = new Date(y, m, 1)
  const count = Math.ceil((first.getDay() + new Date(y, m + 1, 0).getDate()) / 7), today = ymd(new Date())
  const evs = props.events.filter(e => e.start).map(e => ({ ...e, end: e.end || e.start }))
    .sort((a, b) => a.start.localeCompare(b.start) || b.end.localeCompare(a.end))
  return Array.from({ length: count }, (_, w) => {
    const days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(y, m, 1 - first.getDay() + w * 7 + i)
      return { date, key: ymd(date), inMonth: date.getMonth() === m, today: ymd(date) === today }
    })
    const ws = days[0].key, we = days[6].key, lanes = [], segs = [], more = Array(7).fill(0)
    for (const e of evs) {
      if (e.end < ws || e.start > we) continue
      const from = e.start < ws ? 0 : days.findIndex(d => d.key === e.start), to = e.end > we ? 6 : days.findIndex(d => d.key === e.end)
      let lane = lanes.findIndex(l => l.every(([a, b]) => to < a || from > b))
      if (lane < 0) { lane = lanes.length; lanes.push([]) }
      if (lane >= props.maxLanes) { for (let i = from; i <= to; i++) more[i]++; continue }
      lanes[lane].push([from, to])
      segs.push({ ...e, from, to, lane, tone: CATEGORY[e.category]?.tone ?? 'gray', cont: e.start < ws, open: e.end > we })
    }
    return { days, segs, more, lanes: Math.min(lanes.length, props.maxLanes) }
  })
})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.bar strong { font-size: 17px; font-weight: 800; letter-spacing: -.03em; }
.ctrl { display: flex; gap: 6px; }
.ctrl button { padding: 6px 14px; font-size: 14px; }
.ctrl .sq { width: 38px; padding: 0; display: grid; place-items: center; }
.scroll { overflow-x: auto; border-top: 1px solid var(--line); }
.head, .week { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
.ev, .num { max-width: 100%; }
.head span { padding: 6px 8px; font-size: 12px; color: var(--faint); text-align: center; border-bottom: 1px solid var(--line); }
.week { position: relative; min-height: 108px; border-bottom: 1px solid var(--line); }
.day { grid-row: 1 / -1; border-right: 1px solid var(--line); padding: 4px 8px; text-align: right; }
.day:nth-child(7) { border-right: 0; }
.day.weekend { background: #fbfbfa; }
.num { display: inline-grid; place-items: center; min-width: 24px; height: 24px; padding: 0 4px; border-radius: 12px; font-size: 13px; color: var(--muted); }
.day.out .num { color: #c7c6c3; }
.num.today { background: var(--cta); color: #fff; font-weight: 700; }
.ev { position: relative; z-index: 1; margin: 1px 4px; padding: 0 8px; border-radius: 6px; font-size: 12.5px; font-weight: 600; line-height: 24px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-decoration: none; box-shadow: 0 0 0 1px rgba(15, 15, 15, .06), 0 1px 2px rgba(15, 15, 15, .08); }
.ev:hover { filter: brightness(.97); }
.ev.cont { margin-left: 0; border-top-left-radius: 0; border-bottom-left-radius: 0; }
.ev.open { margin-right: 0; border-top-right-radius: 0; border-bottom-right-radius: 0; }
@media (max-width: 640px) {
  .head, .week { grid-template-columns: repeat(7, minmax(0, 1fr)); min-width: 0; }
  .week { min-height: 76px; }
  .day { padding: 2px 3px; }
  .num { min-width: 20px; height: 20px; font-size: 11.5px; padding: 0 2px; }
  .ev { margin: 1px 1px; padding: 0 3px; font-size: 10.5px; line-height: 20px; }
}
.board-bar { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 12px; }
.board-bar .section-title { margin: 0; white-space: nowrap; }
.ym { margin-left: 8px; font-size: 17px; font-weight: 600; }
.board-ctrl { display: flex; gap: 6px; }
.board-ctrl button { padding: 6px 14px; font-size: 14px; white-space: nowrap; }
.board-ctrl .sq { width: 40px; padding: 0; display: grid; place-items: center; }
.compact .scroll { border: 1px solid var(--line); border-radius: 12px; }
.compact .head, .compact .week { grid-template-columns: repeat(7, minmax(0, 1fr)); min-width: 0; }
.compact .week { min-height: 76px; }
.compact .week:last-child { border-bottom: 0; }
.compact .day { padding: 3px 5px; }
.compact .num { min-width: 22px; height: 22px; font-size: 12.5px; }
.compact .ev { margin: 1px 2px; padding: 0 5px; font-size: 11px; line-height: 22px; }
.more { z-index: 1; padding: 0 8px; font-size: 11.5px; color: var(--faint); }
</style>
