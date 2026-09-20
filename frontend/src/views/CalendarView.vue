<template>
  <div class="cal">
    <PageHero tagline="좋아하는 걸, 더 가까운 일상으로." title="내 일정" sub="소중한 경험들이 모여, 더 특별한 하루가 돼요.">
      <template #action><button class="add primary" @click="editor = { mode: 'new' }"><Plus :size="20" :stroke-width="2.4" />새 일정 추가</button></template>
    </PageHero>

    <!-- 요약 줄 -->
    <div class="card strip">
      <a href="#upcoming" class="stat">
        <span class="ic"><CalendarDays :size="24" /></span>
        <span><b>다가오는 일정 <em>{{ upcoming.length }}개</em></b><small>이번 달에 {{ monthItems.length }}개의 일정이 있어요.</small></span>
        <ChevronRight :size="20" class="go" />
      </a>
      <RouterLink to="/map" class="stat">
        <span class="ic"><MapPin :size="24" /></span>
        <span><b>방문할 장소 <em>{{ visitPlaces.length }}곳</em></b><small>{{ placeBreakdown || '장소가 있는 다가오는 일정이 없어요' }}</small></span>
        <ChevronRight :size="20" class="go" />
      </RouterLink>
      <div class="month-nav">
        <button class="ghost sq" aria-label="이전 달" @click="shiftMonth(-1)"><ChevronLeft :size="18" /></button>
        <select :value="monthKey" aria-label="월 선택" @change="month = new Date($event.target.value + '-01T00:00')">
          <option v-for="m in monthOptions" :key="m.key" :value="m.key">{{ m.label }}</option>
        </select>
        <button class="ghost sq" aria-label="다음 달" @click="shiftMonth(1)"><ChevronRight :size="18" /></button>
      </div>
    </div>

    <div class="grid">
      <div class="col">
        <section class="card block month-card"><NotionCalendar v-model:month="month" :events="filteredMonth" :max-lanes="3" /></section>
      </div>
      <div class="col">
        <section id="upcoming" class="card block up-card">
          <div class="hd">
            <h2 class="section-title">다가오는 일정 <small v-if="filteredUpcoming.length">{{ filteredUpcoming.length }}개</small></h2>
            <RouterLink to="/items" class="more-link">전체보기<ChevronRight :size="16" /></RouterLink>
          </div>
          <!-- 카테고리 필터: 캘린더와 목록에 함께 적용 -->
          <div class="chips">
            <button :class="{ on: !filter }" @click="setFilter('')">전체 <em>{{ items.length }}</em></button>
            <button v-for="c in presentCats" :key="c.key" class="tag" :class="[`tone-${c.tone}`, { on: filter === c.key }]" @click="setFilter(filter === c.key ? '' : c.key)">
              {{ c.label }} <em>{{ counts[c.key] }}</em>
            </button>
          </div>
          <div class="list">
          <div v-for="u in pageItems" :key="u.id" class="up">
            <span class="dbox"><b>{{ md(u.start) }}</b><small>{{ wd(u.start) }}</small></span>
            <span class="th"><img v-if="u.image" :src="u.image" alt="" referrerpolicy="no-referrer" @error="u.image = null" /><CategoryArt v-else :kind="u.category" fill /></span>
            <RouterLink :to="`/items/${u.id}`" class="txt">
              <small>{{ periodLabel(u.start, u.end) }}</small>
              <b>{{ u.title }}</b>
              <small v-if="u.place" class="pl"><MapPin :size="13" />{{ u.place.address || u.place.name }}</small>
            </RouterLink>
            <span class="tag" :class="`tone-${CATEGORY[u.category]?.tone ?? 'gray'}`">{{ CATEGORY[u.category]?.label ?? '기타' }}</span>
            <div class="more">
              <button class="text" :aria-label="`${u.title} 메뉴`" @click.stop="menu = menu === u.id ? '' : u.id"><Ellipsis :size="20" /></button>
              <div v-if="menu === u.id" class="menu" @click.stop>
                <RouterLink :to="`/items/${u.id}`"><Eye :size="16" />상세 보기</RouterLink>
                <button class="text" @click="editor = { mode: 'date', item: u }; menu = ''"><Pencil :size="16" />날짜 수정</button>
                <button class="text danger" @click="remove(u)"><Trash2 :size="16" />삭제</button>
              </div>
            </div>
          </div>
          <p v-if="loaded && !filteredUpcoming.length" class="empty">다가오는 일정이 없어요.</p>
          </div>
          <!-- 페이지가 하나여도 자리를 유지해 박스 높이가 흔들리지 않게 -->
          <div class="pager" :class="{ hide: pages <= 1 }">
            <button class="ghost sq" :disabled="page === 0" aria-label="이전 5개" @click="page--"><ChevronLeft :size="18" /></button>
            <span>{{ page + 1 }} / {{ pages }}</span>
            <button class="ghost sq" :disabled="page >= pages - 1" aria-label="다음 5개" @click="page++"><ChevronRight :size="18" /></button>
          </div>
        </section>
      </div>
    </div>

    <ItemEditor v-if="editor" :mode="editor.mode" :item="editor.item" @close="editor = null" @saved="editor = null; load()" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, CalendarDays, MapPin, ChevronLeft, ChevronRight, Ellipsis, Eye, Pencil, Trash2 } from 'lucide-vue-next'
import { getItems, getCalendar, deleteItem } from '../api/nexto'
import { CATEGORIES, CATEGORY } from '../utils/labels'
import { periodLabel, fromItem, fromCalendar, mergeById, monthRange, ymd } from '../utils/events'
import PageHero from '../components/PageHero.vue'
import NotionCalendar from '../components/NotionCalendar.vue'
import CategoryArt from '../components/CategoryArt.vue'
import ItemEditor from '../components/ItemEditor.vue'

const W = ['일', '월', '화', '수', '목', '금', '토']
// ?month=YYYY-MM 으로 들어오면 그 달부터 (검토 화면에서 저장 직후)
const route = useRoute()
const month = ref(/^\d{4}-\d{2}$/.test(route.query.month ?? '') ? new Date(route.query.month + '-01T00:00') : new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const PAGE = 5
const items = ref([]), monthEvents = ref([]), filter = ref(''), loaded = ref(false), editor = ref(null), menu = ref(''), page = ref(0)
const today = ymd(new Date())

const monthKey = computed(() => ymd(month.value).slice(0, 7))
const monthOptions = computed(() => Array.from({ length: 25 }, (_, i) => {
  const d = new Date(month.value.getFullYear(), month.value.getMonth() - 12 + i, 1)
  return { key: ymd(d).slice(0, 7), label: `${d.getFullYear()}년 ${d.getMonth() + 1}월` }
}))
const shiftMonth = n => { month.value = new Date(month.value.getFullYear(), month.value.getMonth() + n, 1) }

const counts = computed(() => items.value.reduce((a, i) => ({ ...a, [i.category]: (a[i.category] ?? 0) + 1 }), {}))
const presentCats = computed(() => CATEGORIES.filter(c => counts.value[c.key]))
const upcoming = computed(() => items.value.filter(i => i.start && (i.end || i.start) >= today).sort((a, b) => a.start.localeCompare(b.start)))
const filteredUpcoming = computed(() => upcoming.value.filter(i => !filter.value || i.category === filter.value))
// 5개씩 좌우로 넘김, 필터가 바뀌면 첫 장으로
const pages = computed(() => Math.max(1, Math.ceil(filteredUpcoming.value.length / PAGE)))
const pageItems = computed(() => filteredUpcoming.value.slice(page.value * PAGE, page.value * PAGE + PAGE))
const setFilter = v => { filter.value = v; page.value = 0 }
watch(pages, n => { if (page.value > n - 1) page.value = Math.max(0, n - 1) })
const monthItems = computed(() => monthEvents.value)
const filteredMonth = computed(() => monthEvents.value.filter(e => !filter.value || e.category === filter.value))
const visitPlaces = computed(() => [...new Map(upcoming.value.filter(i => i.place?.name).map(i => [i.place.name, i])).values()])
const placeBreakdown = computed(() => Object.entries(visitPlaces.value.reduce((a, i) => ({ ...a, [i.category]: (a[i.category] ?? 0) + 1 }), {}))
  .map(([k, n]) => `${CATEGORY[k]?.label ?? '기타'} ${n}`).join(' · '))

const md = s => { const [, m, d] = s.split('-'); return `${+m}.${+d}` }
const wd = s => W[new Date(s + 'T00:00').getDay()]

async function loadMonth() { monthEvents.value = mergeById((await getCalendar(...monthRange(month.value))).map(fromCalendar)) }
async function load() {
  items.value = (await getItems()).map(fromItem); loaded.value = true
  await loadMonth()
}
async function remove(u) {
  menu.value = ''
  if (!confirm(`'${u.title}'을(를) 삭제할까요? 캘린더에서도 사라져요.`)) return
  await deleteItem(u.id); load()
}
const closeMenu = () => (menu.value = '')
watch(month, loadMonth)
onMounted(() => { load(); document.addEventListener('click', closeMenu) })
onBeforeUnmount(() => document.removeEventListener('click', closeMenu))
</script>

<style scoped>
.cal { display: grid; gap: 18px; }
.add { display: inline-flex; align-items: center; gap: 8px; height: 48px; padding: 0 22px; border-radius: 14px; font-size: 15.5px; }
.strip { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; margin: 0; padding: 12px; }
.stat { display: flex; align-items: center; gap: 16px; padding: 12px 18px; border-radius: 12px; background: var(--soft); text-decoration: none; }
.stat:hover { background: var(--hover); }
.stat .ic { flex: none; display: grid; place-items: center; width: 48px; height: 48px; border-radius: 14px; background: var(--grad-soft); color: var(--accent); }
.stat > span:nth-child(2) { flex: 1; display: grid; }
.stat b { font-size: 15px; }
.stat em { margin-left: 8px; font-style: normal; font-size: 19px; font-weight: 800; background: var(--cta); -webkit-background-clip: text; background-clip: text; color: transparent; }
.stat small { font-size: 13px; color: var(--muted); }
.stat .go { color: var(--faint); }
.month-nav { display: flex; align-items: center; gap: 8px; padding: 0 8px; border-radius: 12px; background: var(--soft); }
.month-nav select { width: 170px; font-weight: 600; }
.sq { width: 40px; height: 40px; padding: 0; display: grid; place-items: center; }
/* 두 열 높이를 맞춰 캘린더 카드와 '카테고리로 보기' 카드의 아래 끝을 정렬 */
.grid { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(0, 1fr); gap: 18px; align-items: stretch; }
.cal > * { min-width: 0; }
.col { display: flex; flex-direction: column; gap: 18px; min-width: 0; }
.col > :last-child { flex: 1; }
.block { margin: 0; padding: 20px 22px; }
.hd { display: flex; justify-content: space-between; align-items: center; }
.up-card { display: flex; flex-direction: column; }
/* 5행 높이를 확보해 필터로 항목이 줄어도 박스가 흔들리지 않게 */
.list { flex: 1; min-height: 438px; }
.pager { display: flex; justify-content: center; align-items: center; gap: 12px; padding-top: 10px; font-size: 13.5px; color: var(--muted); }
.pager.hide { visibility: hidden; }
.up { display: grid; grid-template-columns: 58px 72px 1fr auto auto; gap: 12px; align-items: center; padding: 10px; margin-bottom: 8px; border: 1px solid var(--line); border-radius: 12px; }
.dbox { display: grid; place-items: center; align-content: center; height: 58px; border-radius: 14px; background: var(--grad-soft); color: var(--accent); }
.dbox b { font-size: 16px; }
.dbox small { font-size: 12px; }
.th { width: 72px; height: 58px; border-radius: 12px; overflow: hidden; }
.th img, .th :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.txt { display: grid; min-width: 0; text-decoration: none; }
.txt b { font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.txt small { font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.more { position: relative; }
.more > button { font-size: 18px; }
.menu { position: absolute; right: 0; top: 34px; z-index: 20; display: grid; min-width: 130px; padding: 6px; background: #fff; border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 10px 26px rgba(30, 50, 100, .14); }
.menu a, .menu button { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 10px; text-align: left; font-size: 14px; text-decoration: none; color: var(--ink); }
.pl { display: inline-flex; align-items: center; gap: 4px; }
.menu a:hover { background: var(--hover); }
.menu .danger { color: var(--i-red); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.chips button { padding: 7px 16px; border-radius: 999px; border: 1.5px solid transparent; font-size: 14px; font-weight: 600; background: var(--hover); color: var(--ink-2); }
.chips button.on { border-color: var(--ink); background: #fff; color: var(--ink); }
.chips em { font-style: normal; margin-left: 6px; font-weight: 500; opacity: .8; }
@media (max-width: 1280px) { .grid { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 900px) { .strip { grid-template-columns: 1fr; } .month-nav { justify-content: center; padding: 8px; } }
@media (max-width: 560px) {
  .up { grid-template-columns: 52px 1fr auto; }
  .up .th, .up .tag { display: none; }
}
</style>
