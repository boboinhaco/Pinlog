<template>
  <div class="home">
    <!-- 링크 입력 히어로 -->
    <section class="hero">
      <p class="hand tag-line">좋아하는 걸, 더 가까운 일상으로.</p>
      <h1><span class="grad-text">{{ BRAND }}</span></h1>
      <p class="sub">{{ TAGLINE }}</p>
      <LinkBar id="link" :notice="addedNotice" class="linkbar" />
      <div class="doodle" aria-hidden="true">
        <p class="hand">여행도, 일상도<br>기억하고 싶은 모든 순간을<br>{{ BRAND_KO }}와 함께!</p>
        <svg width="70" height="60" viewBox="0 0 70 60" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M40 20 L66 8 L52 34 L46 24 Z" /><path d="M46 24 L66 8" /><path d="M40 22 C 26 34 20 44 4 50" stroke-dasharray="3 4" /></svg>
      </div>
    </section>

    <!-- 추출된 일정 -->
    <section class="card block">
      <div class="head">
        <h2 class="section-title"><CalendarDays :size="24" />추출된 일정 <small>{{ items.length }}개의 일정이 추출되었어요!</small></h2>
        <RouterLink to="/items" class="more-link">전체보기<ChevronRight :size="16" /></RouterLink>
      </div>
      <!-- 카테고리 필터: 인스타 스토리 버블 -->
      <div class="stories" role="tablist" aria-label="카테고리 필터">
        <button role="tab" :aria-selected="!filter" class="story" :class="{ on: !filter }" @click="filter = ''">
          <span class="sring"><span class="sin all"><LayoutGrid :size="24" /></span></span><small>전체</small>
        </button>
        <button v-for="c in presentCats" :key="c.key" role="tab" :aria-selected="filter === c.key" class="story" :class="{ on: filter === c.key }" @click="filter = c.key">
          <span class="sring"><span class="sin"><CategoryArt :kind="c.key" fill /></span></span><small>{{ c.label }}</small>
        </button>
      </div>
      <div class="cards">
        <EventCard v-for="i in shown" :key="i.id" :item="i" @liked="v => (i.liked = v)" />
      </div>
      <p v-if="loaded && !items.length" class="empty">아직 추출한 일정이 없어요. 위에 SNS 링크를 붙여넣어 보세요.</p>
    </section>

    <div class="duo">
      <!-- 저장된 장소 -->
      <section class="card block">
        <div class="head">
          <h2 class="section-title"><MapPin :size="24" />저장된 장소 <small>{{ places.length }}개의 장소가 저장되어 있어요!</small></h2>
          <RouterLink to="/map" class="more-link">전체보기<ChevronRight :size="16" /></RouterLink>
        </div>
        <div class="places">
          <div class="map-box">
            <PlaceMap :places="places" height="100%" />
            <RouterLink to="/map" class="big-map">
              <MapIcon :size="16" />지도로 크게 보기
            </RouterLink>
          </div>
          <div class="plist">
            <RouterLink v-for="p in places.slice(0, 4)" :key="p.name" :to="`/items/${p.items[0].item_id}`" class="place">
              <span class="th"><CategoryArt :kind="p.category" fill /></span>
              <span class="txt"><b>{{ p.name }}</b><small>{{ p.address || p.items[0].title }}</small></span>
              <Bookmark class="bm" :size="18" fill="currentColor" aria-label="저장됨" />
            </RouterLink>
            <p v-if="!places.length" class="empty">장소가 있는 일정을 저장하면 여기에 모여요.</p>
          </div>
        </div>
      </section>

      <!-- 월간 일정표 -->
      <section class="card block"><NotionCalendar v-model:month="month" :events="calEvents" compact :max-lanes="2" /></section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlaces, getItems, getCalendar } from '../api/nexto'
import { CATEGORIES } from '../utils/labels'
import { fromItem, fromCalendar, mergeById, monthRange } from '../utils/events'
import { CalendarDays, MapPin, Map as MapIcon, Bookmark, ChevronRight, LayoutGrid } from 'lucide-vue-next'
import { BRAND, BRAND_KO, TAGLINE } from '../utils/brand'
import LinkBar from '../components/LinkBar.vue'
import EventCard from '../components/EventCard.vue'
import CategoryArt from '../components/CategoryArt.vue'
import PlaceMap from '../components/PlaceMap.vue'
import NotionCalendar from '../components/NotionCalendar.vue'

const route = useRoute(), router = useRouter()
const items = ref([]), places = ref([]), filter = ref(''), loaded = ref(false), addedNotice = ref('')
const month = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1)), calEvents = ref([])
watch(month, async m => { calEvents.value = mergeById((await getCalendar(...monthRange(m))).map(fromCalendar)) }, { immediate: true })

// 최근 저장 순, 필터는 실제로 있는 카테고리만
const presentCats = computed(() => CATEGORIES.filter(c => items.value.some(i => i.category === c.key)))
const shown = computed(() => items.value.filter(i => !filter.value || i.category === filter.value))

onMounted(async () => {
  if (route.query.added) { addedNotice.value = `${route.query.added}건을 일정에 추가했어요.`; router.replace({ query: {} }) }
  const [its, pls] = await Promise.all([getItems(), getPlaces()])
  items.value = its.map(fromItem).sort((a, b) => (b.created ?? '').localeCompare(a.created ?? ''))
  // 장소 썸네일용 카테고리
  const catById = Object.fromEntries(its.map(i => [i.item_id, i.category]))
  places.value = pls.map(p => ({ ...p, category: catById[p.items[0]?.item_id] ?? 'OTHER' }))
  loaded.value = true
})
</script>

<style scoped>
.home { display: grid; gap: 22px; }
.home > *, .duo > * { min-width: 0; }
.hero { position: relative; text-align: center; padding: 6px 0 4px; }
.tag-line { margin: 0; font-size: 24px; color: var(--hand-ink); }
.hero h1 { margin: 2px 0 8px; font-size: clamp(46px, 5.6vw, 68px); font-weight: 800; letter-spacing: -.05em; line-height: 1.1; }
.sub { margin: 0 0 24px; font-size: 17px; color: var(--muted); }
.linkbar { max-width: 980px; margin: 0 auto; }
.doodle { position: absolute; right: 0; top: 20px; color: var(--hand-ink); display: flex; align-items: flex-end; gap: 4px; transform: rotate(-6deg); pointer-events: none; }
.doodle p { margin: 0; font-size: 21px; line-height: 1.25; text-align: left; }
.block { margin: 0; padding: 22px 24px; }
.head { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; margin-bottom: 16px; }
.head .section-title { margin: 0; }
.head .more-link { margin-left: auto; }
.stories { display: flex; gap: 14px; overflow-x: auto; padding: 2px 2px 14px; margin-bottom: 4px; scrollbar-width: none; }
.story { display: grid; justify-items: center; gap: 6px; padding: 0; background: none; color: var(--ink-2); font-weight: 500; flex: none; }
.sring { padding: 2.5px; border-radius: 50%; background: var(--line-strong); transition: background .2s; }
.story.on .sring { background: var(--grad); }
.sin { display: grid; place-items: center; width: 62px; height: 62px; border-radius: 50%; overflow: hidden; border: 3px solid #fff; background: var(--soft); color: var(--ink-2); }
.sin :deep(svg) { width: 100%; height: 100%; display: block; }
.sin.all { background: var(--grad-soft); color: var(--accent); }
.sin.all :deep(svg) { width: 24px; height: 24px; }
.story small { font-size: 12px; }
.story.on small { color: var(--ink); font-weight: 700; }
.story:hover .sring { background: #c7c7c7; }
.story.on:hover .sring { background: var(--grad); }
.cards { display: grid; grid-auto-flow: column; grid-auto-columns: calc((100% - 3 * 16px) / 4); gap: 16px; overflow-x: auto; padding-bottom: 4px; scroll-snap-type: x mandatory; }
.cards > * { scroll-snap-align: start; }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; align-items: stretch; }
.places { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; height: 260px; }
.map-box { position: relative; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }
.big-map { position: absolute; left: 12px; bottom: 12px; z-index: 500; display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; background: rgba(255, 255, 255, .95); backdrop-filter: blur(6px); box-shadow: 0 4px 14px rgba(0, 0, 0, .12); text-decoration: none; font-size: 13px; font-weight: 700; }
.plist { display: grid; align-content: start; overflow-y: auto; }
.place { display: flex; align-items: center; gap: 12px; padding: 8px 4px; border-bottom: 1px solid var(--line); text-decoration: none; }
.place:last-child { border-bottom: 0; }
.place:hover { background: var(--soft); }
.th { flex: none; width: 52px; height: 52px; border-radius: 14px; overflow: hidden; }
.th :deep(svg) { width: 100%; height: 100%; display: block; }
.txt { flex: 1; min-width: 0; display: grid; }
.txt b { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.txt small { font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bm { flex: none; color: var(--ink); }
@media (max-width: 1400px) { .doodle { display: none; } }
@media (max-width: 1280px) { .duo { grid-template-columns: 1fr; } }
@media (max-width: 1100px) { .cards { grid-auto-columns: calc((100% - 2 * 16px) / 3); } }
@media (max-width: 760px) {
  .cards { grid-auto-columns: 78%; }
  .places { grid-template-columns: 1fr; height: auto; }
  .map-box { height: 240px; }
  .tag-line { font-size: 20px; }
  .sub { font-size: 15px; }
}
</style>
