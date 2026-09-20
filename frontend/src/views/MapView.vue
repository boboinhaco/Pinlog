<template>
  <div class="places-page">
    <PageHero tagline="좋아하는 곳이, 더 가까운 일상으로." title="저장한 장소" sub="언제든 다시 가고 싶은 장소들을 지도로 한눈에 확인하고, 소중한 순간을 계획해보세요."
              doodle="지도 위의<br>나만의 취향 지도를<br>만들어보세요!" />

    <!-- 검색·필터 -->
    <div class="tools">
      <label class="search">
        <Search :size="20" />
        <input v-model="q" placeholder="저장한 장소를 검색해보세요. (예: 송파구, 페스티벌, 전시회)" aria-label="장소 검색" />
      </label>
      <select v-model="cat" aria-label="카테고리"><option value="">전체 카테고리</option><option v-for="c in presentCats" :key="c.key" :value="c.key">{{ c.label }}</option></select>
      <select v-model="region" aria-label="지역"><option value="">지역</option><option v-for="r in regions" :key="r" :value="r">{{ r }}</option></select>
      <button class="ghost view" @click="listOnly = !listOnly"><component :is="listOnly ? MapIcon : List" :size="17" />{{ listOnly ? '지도 보기' : '리스트 보기' }}</button>
    </div>

    <div class="tabs-row">
      <div class="tabs" role="tablist">
        <button v-for="t in TABS" :key="t.key" role="tab" :aria-selected="tab === t.key" :class="{ on: tab === t.key }" @click="tab = t.key">
          {{ t.label }}<small>{{ tabCount(t.key) }}</small>
        </button>
      </div>
      <div class="chips">
        <button :class="{ on: !cat }" @click="cat = ''">전체</button>
        <button v-for="c in presentCats" :key="c.key" :class="{ on: cat === c.key }" @click="cat = cat === c.key ? '' : c.key"><i :style="{ background: pinColor(c.key) }"></i>{{ c.label }}</button>
      </div>
    </div>

    <div class="body" :class="{ 'list-only': listOnly }">
      <div v-if="!listOnly" class="map-col"><PlacesMap :places="filtered" :selected="selected" @select="n => (selected = n)" /></div>
      <section class="list">
        <div class="hd">
          <h2 class="section-title">저장한 장소 <small>{{ filtered.length }}개</small></h2>
          <select v-model="sort" aria-label="정렬"><option value="recent">최근 저장순</option><option value="name">이름순</option><option value="date">일정 날짜순</option></select>
        </div>
        <div class="cards">
          <div v-for="p in sorted.slice(0, limit)" :key="p.name" class="pc" :class="{ on: selected === p.name }" @click="selected = p.name">
            <span class="th"><img v-if="p.image" :src="p.image" alt="" referrerpolicy="no-referrer" @error="p.image = null" /><CategoryArt v-else :kind="p.category" fill /></span>
            <div class="txt">
              <b>{{ p.name }}</b>
              <div class="tags">
                <span class="tag" :class="`tone-${CATEGORY[p.category]?.tone ?? 'gray'}`">{{ CATEGORY[p.category]?.label ?? '기타' }}</span>
                <span v-if="p.thisWeek" class="tag tone-red"><Clock :size="12" />이번 주 일정</span>
                <span v-else-if="p.linked" class="tag tone-blue"><CalendarDays :size="12" />일정 연결됨</span>
                <span v-if="p.liked" class="tag tone-yellow"><Star :size="12" fill="currentColor" />즐겨찾기</span>
              </div>
              <small class="addr"><MapPin :size="13" />{{ p.address || '주소 미상' }}</small>
            </div>
            <div class="side">
              <button class="heart" :class="{ on: p.liked }" :aria-pressed="p.liked" :aria-label="p.liked ? '즐겨찾기 해제' : '즐겨찾기'" @click.stop="toggleLike(p)">
                <Heart :size="20" :stroke-width="2" :fill="p.liked ? 'currentColor' : 'none'" />
              </button>
              <RouterLink :to="`/items/${p.items[0].id}`" class="go" aria-label="상세 보기" @click.stop><ChevronRight :size="18" /></RouterLink>
              <small>{{ savedLabel(p.created) }} 저장</small>
            </div>
          </div>
          <p v-if="loaded && !filtered.length" class="empty">{{ places.length ? '조건에 맞는 장소가 없어요.' : '장소가 있는 일정을 저장하면 여기에 모여요.' }}</p>
        </div>
        <button v-if="sorted.length > limit" class="ghost more" @click="limit += 5">더 많은 장소 보기<ChevronDown :size="16" /></button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, List, Map as MapIcon, MapPin, Clock, CalendarDays, Star, ChevronRight, ChevronDown, Heart } from 'lucide-vue-next'
import { getItems, patchItem } from '../api/nexto'
import { CATEGORIES, CATEGORY, pinColor } from '../utils/labels'
import { fromItem, ymd } from '../utils/events'
import PageHero from '../components/PageHero.vue'
import PlacesMap from '../components/PlacesMap.vue'
import CategoryArt from '../components/CategoryArt.vue'

const TABS = [{ key: 'all', label: '전체' }, { key: 'recent', label: '최근 저장' }, { key: 'linked', label: '일정 연결' }, { key: 'liked', label: '즐겨찾기' }]
const items = ref([]), loaded = ref(false), q = ref(''), cat = ref(''), region = ref(''), tab = ref('all'), sort = ref('recent')
const listOnly = ref(false), selected = ref(''), limit = ref(5)

// 저장 항목 → 장소 (장소명 기준으로 묶음)
const places = computed(() => {
  const today = ymd(new Date()), weekEnd = ymd(new Date(Date.now() + 7 * 86400000)), weekAgo = new Date(Date.now() - 7 * 86400000).toISOString()
  const map = new Map()
  for (const i of items.value) {
    if (!i.place?.name) continue
    const p = map.get(i.place.name) ?? { name: i.place.name, address: i.place.address, lat: i.place.lat, lng: i.place.lng, category: i.category, image: i.image, items: [], created: '' }
    p.items.push(i)
    if ((i.created ?? '') > p.created) p.created = i.created ?? ''
    map.set(p.name, p)
  }
  return [...map.values()].map(p => ({
    ...p, liked: p.items.some(i => i.liked), linked: p.items.some(i => i.start),
    thisWeek: p.items.some(i => i.start && i.start <= weekEnd && (i.end || i.start) >= today), recent: p.created >= weekAgo,
    region: regionOf(p.address), first: p.items.map(i => i.start).filter(Boolean).sort()[0] ?? '9999'
  }))
})
const regionOf = a => (a ?? '').split(/\s+/).slice(0, 2).join(' ') || '기타'
const regions = computed(() => [...new Set(places.value.map(p => p.region))].sort())
const presentCats = computed(() => CATEGORIES.filter(c => places.value.some(p => p.category === c.key)))
const inTab = (p, t) => t === 'all' || (t === 'recent' && p.recent) || (t === 'linked' && p.linked) || (t === 'liked' && p.liked)
const tabCount = t => places.value.filter(p => inTab(p, t)).length
const filtered = computed(() => places.value.filter(p => inTab(p, tab.value) && (!cat.value || p.category === cat.value) && (!region.value || p.region === region.value)
  && (!q.value.trim() || [p.name, p.address, ...p.items.map(i => i.title)].join(' ').includes(q.value.trim()))))
const sorted = computed(() => [...filtered.value].sort((a, b) =>
  sort.value === 'name' ? a.name.localeCompare(b.name) : sort.value === 'date' ? a.first.localeCompare(b.first) : b.created.localeCompare(a.created)))
const savedLabel = c => { if (!c) return ''; const d = new Date(c); return `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.` }

// 즐겨찾기 = 그 장소의 일정들에 좋아요
async function toggleLike(p) {
  const v = !p.liked
  await Promise.all(p.items.map(i => patchItem(i.id, { fields: { liked: v } })))
  p.items.forEach(i => { const it = items.value.find(x => x.id === i.id); if (it) it.liked = v })
}
onMounted(async () => { items.value = (await getItems()).map(fromItem); loaded.value = true })
</script>

<style scoped>
.places-page { display: grid; gap: 16px; }
.tools { display: grid; grid-template-columns: 1fr 190px 150px auto; gap: 12px; }
.search { display: flex; align-items: center; gap: 12px; padding: 0 18px; background: #fff; border: 1px solid var(--line-strong); border-radius: 14px; box-shadow: var(--shadow); }
.search input { border: 0; padding: 14px 0; font-size: 15px; }
.search input:focus { outline: none; }
.tools select { height: 100%; min-height: 50px; border-radius: 14px; font-weight: 600; }
.view { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border-radius: 14px; font-weight: 600; padding: 0 20px; }
.tabs-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 20px; }
.tabs { display: flex; background: #fff; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
.tabs button { display: grid; min-width: 104px; padding: 6px 18px; border-radius: 0; background: none; color: var(--ink-2); font-weight: 600; }
.tabs button small { font-weight: 500; color: var(--muted); }
.tabs button.on { background: var(--cta); color: #fff; }
.tabs button.on small { color: #fff; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chips button { display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 999px; background: #fff; color: var(--ink-2); border: 1px solid var(--line); font-size: 13.5px; font-weight: 500; }
.chips button.on { background: var(--accent-deep); color: #fff; border-color: transparent; }
.chips i { width: 10px; height: 10px; border-radius: 3px; }
.body { display: grid; grid-template-columns: 1.45fr 1fr; gap: 18px; align-items: stretch; }
.body.list-only { grid-template-columns: 1fr; }
.map-col { min-height: 560px; }
.list { min-width: 0; }
.hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.hd .section-title { margin: 0; }
.hd select { width: auto; border-radius: 10px; }
.cards { display: grid; gap: 10px; }
.list-only .cards { grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); }
.pc { display: grid; grid-template-columns: 116px 1fr auto; gap: 14px; align-items: center; padding: 8px; background: #fff; border: 1px solid var(--line); border-radius: 14px; cursor: pointer; box-shadow: var(--shadow); }
.pc:hover { border-color: var(--line-strong); }
.pc.on { border-color: var(--accent); box-shadow: 0 0 0 2px var(--focus); }
.th { height: 78px; border-radius: 10px; overflow: hidden; }
.th img, .th :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.txt { display: grid; gap: 4px; min-width: 0; }
.txt b { font-size: 15.5px; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
.tags .tag { font-size: 11.5px; padding: 1px 8px; border-radius: 6px; }
.txt small { font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.side { display: grid; justify-items: end; align-content: space-between; height: 100%; gap: 4px; padding-right: 6px; }
.side small { font-size: 11.5px; color: var(--faint); white-space: nowrap; }
.heart { padding: 2px; background: none; color: var(--muted); }
.go { color: var(--faint); text-decoration: none; line-height: 1; }
.addr { display: inline-flex; align-items: center; gap: 4px; }
.heart.on { color: var(--accent); }
.more { width: 100%; margin-top: 10px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
@media (max-width: 1200px) { .body { grid-template-columns: 1fr; } .map-col { min-height: 420px; } }
@media (max-width: 760px) {
  .tools { grid-template-columns: 1fr 1fr; }
  .search { grid-column: 1 / -1; }
  .view { grid-column: 1 / -1; min-height: 44px; }
  .tabs { width: 100%; } .tabs button { flex: 1; min-width: 0; padding: 6px 4px; }
  .pc { grid-template-columns: 84px 1fr auto; }
  .th { height: 64px; }
  .list-only .cards { grid-template-columns: 1fr; }
}
</style>
