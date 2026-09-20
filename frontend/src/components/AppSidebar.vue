<template>
  <aside ref="root" class="side">
    <div class="top">
      <RouterLink to="/home" class="brand" aria-label="Pinlog 홈"><PinLogo :size="30" /></RouterLink>
      <div class="pop-wrap">
        <button class="icon" :class="{ on: open === 'bell' }" aria-label="다가오는 일정 알림" @click="toggle('bell')">
          <Bell :size="20" :stroke-width="1.9" /><i v-if="upcoming.length" class="dot">{{ upcoming.length }}</i>
        </button>
        <div v-if="open === 'bell'" class="pop">
          <p class="pop-title">다가오는 일정</p>
          <RouterLink v-for="u in upcoming" :key="u.id" :to="`/items/${u.id}`" class="row" @click="open = ''">
            <span class="thumb" :class="`tone-${CATEGORY[u.category]?.tone ?? 'gray'}`"><Clock :size="15" /></span>
            <span><b>{{ u.title }}</b><small>{{ u.label }}</small></span>
          </RouterLink>
          <p v-if="!upcoming.length" class="none">7일 안에 다가오는 일정이 없어요.</p>
        </div>
      </div>
    </div>

    <!-- 검색 (⌘K) -->
    <div class="pop-wrap search-wrap">
      <label class="sbox">
        <Search :size="16" />
        <input ref="searchEl" v-model="q" placeholder="저장한 일정·장소 검색" @focus="open = 'search'" @keydown.escape="open = ''" />
        <kbd>⌘K</kbd>
      </label>
      <div v-if="open === 'search'" class="pop wide">
        <RouterLink v-for="i in results" :key="i.id" :to="`/items/${i.id}`" class="row" @click="open = ''">
          <span class="thumb" :class="`tone-${CATEGORY[i.category]?.tone ?? 'gray'}`"><CalendarDays :size="15" /></span>
          <span><b>{{ i.title }}</b><small>{{ periodLabel(i.start, i.end) }}<template v-if="i.place"> · {{ i.place.name }}</template></small></span>
        </RouterLink>
        <p v-if="q && !results.length" class="none">'{{ q }}'에 맞는 항목이 없어요.</p>
      </div>
    </div>

    <nav class="nav">
      <RouterLink v-for="n in NAV" :key="n.to" :to="n.to" :class="{ on: isOn(n) }">
        <component :is="n.icon" :size="20" :stroke-width="isOn(n) ? 2.4 : 1.9" :fill="isOn(n) && n.fill ? 'currentColor' : 'none'" />{{ n.label }}
      </RouterLink>
    </nav>

    <!-- 최근 저장한 항목 -->
    <section v-if="recent.length" class="grp">
      <h3>최근 항목</h3>
      <RouterLink v-for="i in recent" :key="i.id" :to="`/items/${i.id}`" class="rc">
        <span class="th"><img v-if="i.image" :src="i.image" alt="" referrerpolicy="no-referrer" @error="i.image = null" /><CategoryArt v-else :kind="i.category" fill /></span>
        <span class="t">{{ i.title }}</span>
      </RouterLink>
    </section>

    <button class="cal-card" :disabled="icsBusy" @click="exportCalendar">
      <span class="ci"><CalendarPlus :size="20" /></span>
      <span class="ct"><b>캘린더 연결하기</b><small>{{ icsMsg || '내 모든 일정을 한곳에서' }}</small></span>
      <ChevronRight :size="18" class="chev" />
    </button>

    <!-- 카테고리 (개인 페이지) -->
    <section class="grp">
      <h3>개인 페이지<button class="plus" aria-label="새 일정 추가" @click="addNew"><Plus :size="16" /></button></h3>
      <RouterLink v-for="c in cats" :key="c.key" :to="`/category/${c.key}`" class="ln">
        <Star :size="15" class="star" :fill="route.path === `/category/${c.key}` ? 'currentColor' : 'none'" />
        <span>{{ c.label }}</span><small>{{ c.count }}</small>
      </RouterLink>
      <p v-if="!cats.length" class="none">저장하면 카테고리별로 모여요.</p>
    </section>

    <!-- SNS 출처별 저장함 -->
    <section class="grp">
      <h3>저장된 링크<button class="plus" aria-label="링크 추가" @click="addNew"><Plus :size="16" /></button></h3>
      <RouterLink v-for="s in sources" :key="s.key" :to="{ path: '/items', query: { source: s.key } }" class="ln">
        <i class="src" :style="{ background: s.color }"><component :is="s.icon" :size="11" :stroke-width="2.6" color="#fff" /></i>
        <span>{{ s.label }}</span><small>{{ s.count }}</small>
      </RouterLink>
      <RouterLink to="/items" class="ln more"><Ellipsis :size="15" /><span>더보기</span></RouterLink>
    </section>

    <RouterLink to="/" class="promo">
      <span class="ci"><Sparkles :size="18" /></span>
      <span class="ct"><b>{{ BRAND }}가 하는 일</b><small>서비스 소개와 검증 방식 보기</small></span>
      <ChevronRight :size="18" class="chev" />
    </RouterLink>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, Search, Clock, CalendarDays, House, MapPin, Heart, CalendarPlus, ChevronRight, Plus, Star, Ellipsis, Sparkles, Instagram, Youtube, FileText, Link2 } from 'lucide-vue-next'
import { getItems, downloadIcs } from '../api/nexto'
import { fromItem, periodLabel } from '../utils/events'
import { CATEGORIES, CATEGORY } from '../utils/labels'
import { upcomingOf, searchItems } from '../utils/itemsQuery'
import { sourceOf } from '../utils/source'
import { BRAND } from '../utils/brand'
import PinLogo from './PinLogo.vue'
import CategoryArt from './CategoryArt.vue'

const NAV = [
  { to: '/home', label: '홈', icon: House },
  { to: '/calendar', label: '내 일정', icon: CalendarDays },
  { to: '/map', label: '저장한 장소', icon: MapPin },
  { to: '/liked', label: '좋아요', icon: Heart, fill: true }
]
const SRC_ICON = { instagram: Instagram, youtube: Youtube, blog: FileText, etc: Link2, manual: Link2 }
const route = useRoute(), router = useRouter()
const root = ref(null), searchEl = ref(null), open = ref(''), q = ref(''), items = ref([]), icsBusy = ref(false), icsMsg = ref('')

const isOn = n => route.path === n.to || (n.to === '/calendar' && route.path.startsWith('/items/'))
const toggle = name => (open.value = open.value === name ? '' : name)
const upcoming = computed(() => upcomingOf(items.value))
const results = computed(() => searchItems(items.value, q.value))
const recent = computed(() => [...items.value].sort((a, b) => (b.created ?? '').localeCompare(a.created ?? '')).slice(0, 5))
const cats = computed(() => CATEGORIES.map(c => ({ ...c, count: items.value.filter(i => i.category === c.key).length })).filter(c => c.count).slice(0, 6))
const sources = computed(() => {
  const m = {}
  for (const i of items.value) { const s = sourceOf(i.sourceUrl); if (s.key === 'manual') continue; m[s.key] = m[s.key] ? { ...m[s.key], count: m[s.key].count + 1 } : { ...s, icon: SRC_ICON[s.key], count: 1 } }
  return Object.values(m)
})

const load = async () => { items.value = (await getItems().catch(() => [])).map(fromItem) }
const addNew = () => router.push({ path: '/home', hash: '#link' })
async function exportCalendar() {
  icsBusy.value = true; icsMsg.value = ''
  try { await downloadIcs(); icsMsg.value = 'pinlog.ics 저장됨 · 캘린더 앱에서 열기' } catch { icsMsg.value = '내려받지 못했어요' }
  finally { icsBusy.value = false; setTimeout(() => (icsMsg.value = ''), 4000) }
}
const onDoc = e => { if (root.value && !root.value.contains(e.target)) open.value = '' }
const onKey = e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); searchEl.value?.focus() } }
onMounted(() => { document.addEventListener('click', onDoc); document.addEventListener('keydown', onKey); load() })
watch(() => route.fullPath, () => { open.value = ''; load() })
onBeforeUnmount(() => { document.removeEventListener('click', onDoc); document.removeEventListener('keydown', onKey) })
</script>

<style scoped>
.side { position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto; display: grid; align-content: start; gap: 18px; padding: 18px 16px 24px; background: #fff; border-right: 1px solid var(--line); scrollbar-width: thin; }
.top { display: flex; align-items: center; justify-content: space-between; padding: 0 4px; }
.brand { text-decoration: none; }
.pop-wrap { position: relative; }
.icon { position: relative; display: grid; place-items: center; width: 38px; height: 38px; padding: 0; border-radius: 12px; background: none; color: var(--ink); }
.icon:hover, .icon.on { background: var(--hover); }
.dot { position: absolute; top: 4px; right: 4px; transform: translate(40%, -40%); min-width: 14px; height: 14px; padding: 0 3px; border-radius: 8px; background: #ff3040; color: #fff; font-size: 9.5px; font-style: normal; font-weight: 700; line-height: 14px; border: 2px solid #fff; box-sizing: content-box; }
.pop { position: absolute; left: 0; top: 46px; z-index: 50; width: 300px; padding: 8px; background: #fff; border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow-lg); }
.top .pop { left: auto; right: 0; }
.pop.wide { width: 100%; }
.pop-title { margin: 8px 10px; font-weight: 700; font-size: 14px; }
.row { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 12px; text-decoration: none; }
.row:hover { background: var(--hover); }
.thumb { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; flex: none; }
.row > span:last-child { display: grid; min-width: 0; }
.row b { font-size: 13.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row small { font-size: 12px; color: var(--muted); }
.none { margin: 8px 6px; font-size: 12.5px; color: var(--faint); }
.sbox { display: flex; align-items: center; gap: 8px; padding: 0 12px; border-radius: 12px; background: var(--hover); color: var(--muted); }
.sbox input { border: 0; background: none; padding: 10px 0; font-size: 13.5px; box-shadow: none; }
.sbox input:focus { outline: none; box-shadow: none; }
kbd { font: inherit; font-size: 11px; color: var(--faint); padding: 1px 6px; border: 1px solid var(--line-strong); border-radius: 6px; background: #fff; }
.nav { display: grid; gap: 2px; }
.nav a { display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 12px; text-decoration: none; color: var(--ink-2); font-weight: 500; font-size: 14.5px; }
.nav a:hover { background: var(--hover); }
.nav a.on { background: var(--accent-soft); color: var(--ink); font-weight: 700; }
.nav a.on .lucide { color: var(--accent); }
.grp { display: grid; gap: 2px; padding-top: 14px; border-top: 1px solid var(--line); }
.grp h3 { display: flex; align-items: center; justify-content: space-between; margin: 0 0 6px; padding: 0 4px; font-size: 12.5px; font-weight: 600; color: var(--muted); }
.plus { display: grid; place-items: center; width: 24px; height: 24px; padding: 0; border-radius: 8px; background: none; color: var(--muted); }
.plus:hover { background: var(--hover); color: var(--ink); }
.rc { display: flex; align-items: center; gap: 10px; padding: 6px 6px; border-radius: 10px; text-decoration: none; }
.rc:hover { background: var(--hover); }
.th { flex: none; width: 30px; height: 30px; border-radius: 8px; overflow: hidden; }
.th img, .th :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.t { font-size: 13.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-card, .promo { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 14px; background: var(--grad-soft); color: var(--ink); text-align: left; text-decoration: none; border: 1px solid var(--line); }
.cal-card:hover, .promo:hover { box-shadow: var(--shadow); }
.ci { display: grid; place-items: center; width: 40px; height: 40px; border-radius: 12px; background: #fff; color: var(--accent); flex: none; }
.ct { flex: 1; display: grid; min-width: 0; }
.ct b { font-size: 13.5px; }
.ct small { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chev { color: var(--faint); }
.ln { display: flex; align-items: center; gap: 10px; padding: 8px 8px; border-radius: 10px; text-decoration: none; font-size: 13.5px; font-weight: 500; color: var(--ink-2); }
.ln:hover { background: var(--hover); }
.ln span { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ln small { color: var(--faint); font-size: 12px; }
.ln.more { color: var(--muted); }
.star { color: var(--accent); }
.src { display: grid; place-items: center; width: 20px; height: 20px; border-radius: 6px; }
</style>
