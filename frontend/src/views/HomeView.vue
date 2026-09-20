<template>
  <div class="home">
    <!-- 배너: 화면 폭 전체에 사진을 깔고 왼쪽에 브랜드 문구, 아래는 페이지 배경으로 흐려짐. 링크 입력창은 그 위에 걸침 -->
    <section class="hero">
      <div class="banner">
        <img class="scene" src="/home-bg.jpg" alt="" />
        <div class="shade" aria-hidden="true"></div>
        <div class="hero-text">
          <p class="hand tag-line grad-text">일상이 조금 더 특별해지는 ♡</p>
          <h1 class="grad-text">{{ BRAND }}</h1>
          <p class="sub">{{ tag1 }},<br>{{ tag2 }}</p>
          <ul class="tags" aria-label="이런 것들을 정리해요"><li v-for="t in TAGS" :key="t">#{{ t }}</li></ul>
        </div>
      </div>
      <LinkBar id="link" :notice="addedNotice" class="linkbar" />
    </section>

    <div class="inner">
    <!-- 추출된 일정 -->
    <section class="card block">
      <div class="head">
        <h2 class="section-title"><Sparkles :size="24" />추출한 항목 <small>일정·장소·물품 {{ items.length }}개를 정리했어요!</small></h2>
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
          <h2 class="section-title"><MapPin :size="24" />저장된 장소 <small>가고 싶은 곳을 저장하고, 지도로 한눈에 확인해보세요.</small></h2>
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
              <span class="th"><img v-if="p.image" :src="p.image" alt="" referrerpolicy="no-referrer" @error="p.image = null" /><CategoryArt v-else :kind="p.category" fill /></span>
              <span class="txt"><b>{{ p.name }}</b><small>{{ p.address || p.items[0].title }}</small></span>
              <button class="heart" :class="{ on: p.liked }" :aria-pressed="p.liked" :aria-label="p.liked ? '즐겨찾기 해제' : '즐겨찾기'" @click.prevent.stop="togglePlace(p)">
                <Heart :size="18" :stroke-width="2" :fill="p.liked ? 'currentColor' : 'none'" />
              </button>
            </RouterLink>
            <p v-if="!places.length" class="empty">장소가 있는 일정을 저장하면 여기에 모여요.</p>
          </div>
        </div>
      </section>

      <!-- 다가오는 일정 -->
      <section class="card block">
        <div class="head">
          <h2 class="section-title"><CalendarDays :size="24" />다가오는 일정 <small>이번 달, 놓치지 말아야 할 일정이에요.</small></h2>
          <RouterLink to="/calendar" class="more-link">전체보기<ChevronRight :size="16" /></RouterLink>
        </div>
        <div class="upl">
          <RouterLink v-for="u in upcoming" :key="u.id" :to="`/items/${u.id}`" class="ur">
            <span class="dbox"><b>{{ md(u.start) }}</b><small>{{ wd(u.start) }}</small></span>
            <i class="dot" :style="{ background: pinColor(u.category) }"></i>
            <span class="ut">
              <b>{{ u.title }}</b>
              <small>{{ mdw(u.start) }}<template v-if="u.end && u.end !== u.start"> - {{ mdw(u.end) }}</template></small>
            </span>
            <span v-if="u.place" class="up"><MapPin :size="14" />{{ u.place.name }}</span>
            <span class="tag" :class="daysUntil(u.start) <= 7 ? 'tone-red' : 'tone-pink'">{{ ddayLabel(u.start) }}</span>
          </RouterLink>
          <p v-if="loaded && !upcoming.length" class="empty">다가오는 일정이 없어요. 링크를 넣어 일정을 추가해보세요.</p>
        </div>
      </section>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlaces, getItems, patchItem } from '../api/nexto'
import { CATEGORIES, pinColor } from '../utils/labels'
import { fromItem, mdw } from '../utils/events'
import { activeSorted, daysUntil, ddayLabel } from '../utils/itemsQuery'
import { CalendarDays, MapPin, Map as MapIcon, Heart, ChevronRight, LayoutGrid, Sparkles } from 'lucide-vue-next'
import { BRAND, TAGLINE } from '../utils/brand'
import LinkBar from '../components/LinkBar.vue'
import EventCard from '../components/EventCard.vue'
import CategoryArt from '../components/CategoryArt.vue'
import PlaceMap from '../components/PlaceMap.vue'

// 배너 문구: 태그라인을 쉼표에서 두 줄로, 해시태그는 장식
const [tag1, tag2] = TAGLINE.replace(/\.$/, '').split(', ')
const TAGS = ['공연', '팝업스토어', '전시', '여행', '계절 행사']
const route = useRoute(), router = useRouter()
const items = ref([]), places = ref([]), filter = ref(''), loaded = ref(false), addedNotice = ref('')
const W = ['일', '월', '화', '수', '목', '금', '토']
const md = s => { const [, m, d] = s.split('-'); return `${+m}.${+d}` }
const wd = s => W[new Date(s + 'T00:00').getDay()]
// 아직 끝나지 않은 일정 5개
const upcoming = computed(() => activeSorted(items.value).slice(0, 5))

// 최근 저장 순, 필터는 실제로 있는 카테고리만
const presentCats = computed(() => CATEGORIES.filter(c => items.value.some(i => i.category === c.key)))
const shown = computed(() => items.value.filter(i => !filter.value || i.category === filter.value))

// 장소 즐겨찾기 = 그 장소의 일정들에 좋아요
async function togglePlace(p) {
  const v = !p.liked; p.liked = v
  try { await Promise.all(p.items.map(x => patchItem(x.item_id, { fields: { liked: v } }))); items.value.forEach(i => { if (p.items.some(x => x.item_id === i.id)) i.liked = v }) } catch { p.liked = !v }
}
const focusLink = () => { const el = document.querySelector('#link input'); el?.scrollIntoView({ behavior: 'smooth', block: 'center' }); el?.focus() }

onMounted(async () => {
  if (route.query.added) { addedNotice.value = `${route.query.added}건을 일정에 추가했어요.`; router.replace({ query: {} }) }
  const [its, pls] = await Promise.all([getItems(), getPlaces()])
  items.value = its.map(fromItem).sort((a, b) => (b.created ?? '').localeCompare(a.created ?? ''))
  // 장소 썸네일·즐겨찾기는 그 장소의 일정에서
  const byId = Object.fromEntries(its.map(i => [i.item_id, i]))
  places.value = pls.map(p => {
    const first = byId[p.items[0]?.item_id]
    return { ...p, category: first?.category ?? 'OTHER', image: first?.fields?.image_url ?? null, liked: p.items.some(x => byId[x.item_id]?.fields?.liked) }
  })
  loaded.value = true
  if (route.hash === '#link') focusLink()
})
</script>

<style scoped>
.home { display: block; }   /* grid면 배너의 비율·최소 높이가 가로폭으로 번져 좁은 화면에서 넘침 */
/* 배너 아래 본문은 원래 페이지 폭으로 */
.inner { width: 100%; max-width: 1320px; margin: 0 auto; padding: 26px 32px 64px; display: grid; gap: 22px; }
.inner > *, .duo > * { min-width: 0; }
.hero { position: relative; }
/* 높이를 폭에 비례(약 2.66:1)시켜 화면이 넓어져도 같은 부분이 보이게. 아주 넓거나 좁을 때만 min/max로 제한 */
.banner { position: relative; display: flex; align-items: center; width: 100%; aspect-ratio: 133 / 50; min-height: 380px; max-height: 640px; overflow: hidden; background: #f6e9ec; }
/* 배경 사진(책상 셋업, 모니터·화병이 가운데 오게 자름): 왼쪽 글자 뒤는 흰색으로, 아래쪽은 페이지 배경으로 흐려짐 */
.scene { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 46%; }
.shade { position: absolute; inset: 0; background:
  linear-gradient(180deg, rgba(250, 250, 250, 0) 42%, rgba(250, 250, 250, .72) 80%, var(--bg) 100%),
  linear-gradient(90deg, rgba(255, 255, 255, .96) 0%, rgba(255, 255, 255, .88) 26%, rgba(255, 255, 255, .4) 46%, rgba(255, 255, 255, 0) 62%); }
/* 글자 블록은 본문 폭(1320px) 안에서 왼쪽 정렬: 보통 화면에선 왼쪽 32px, 넓은 화면에선 가운데 쪽으로 들어옴. 세로는 배너 가운데(아래 여백은 링크창 자리) */
.hero-text { position: relative; z-index: 1; width: 100%; max-width: 1320px; margin: 0 auto; padding: 36px 32px 96px; }
.hero-text > * { max-width: 560px; }
.tag-line { display: inline-block; margin: 0 0 2px; font-size: 27px; line-height: 1.1; }
.hero h1 { margin: 0 0 12px; font-size: clamp(46px, 5.6vw, 66px); font-weight: 800; letter-spacing: -.05em; line-height: 1.05; }
.sub { margin: 0 0 16px; font-size: 16px; line-height: 1.55; color: var(--ink-2); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; padding: 0; list-style: none; }
.tags li { padding: 4px 11px; border-radius: 999px; background: rgba(255, 255, 255, .85); border: 1px solid var(--line-strong); font-size: 12.5px; font-weight: 600; color: var(--ink-2); }
.linkbar { position: relative; z-index: 2; max-width: 1012px; margin: -46px auto 0; padding: 0 16px; }
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
.heart { flex: none; display: grid; place-items: center; width: 34px; height: 34px; padding: 0; border-radius: 50%; background: none; color: var(--muted); }
.heart:hover { background: var(--hover); }
.heart.on { color: #ff3040; }
.th img { width: 100%; height: 100%; object-fit: cover; display: block; }
.upl { display: grid; gap: 8px; }
.ur { display: grid; grid-template-columns: 56px 10px 1fr auto auto; gap: 12px; align-items: center; padding: 10px 12px; border: 1px solid var(--line); border-radius: 14px; text-decoration: none; transition: box-shadow .15s; }
.ur:hover { box-shadow: var(--shadow); }
.dbox { display: grid; place-items: center; align-content: center; height: 50px; border-radius: 12px; background: var(--grad-soft); color: var(--accent); }
.dbox b { font-size: 14.5px; }
.dbox small { font-size: 11.5px; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.ut { display: grid; min-width: 0; }
.ut b { font-size: 14.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ut small { font-size: 12.5px; color: var(--muted); }
.up { display: inline-flex; align-items: center; gap: 4px; max-width: 150px; font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 1280px) { .duo { grid-template-columns: 1fr; } }
@media (max-width: 1100px) { .cards { grid-auto-columns: calc((100% - 2 * 16px) / 3); } }
@media (max-width: 760px) {
  .cards { grid-auto-columns: 78%; }
  .ur { grid-template-columns: 50px 1fr auto; }
  .ur .dot, .ur .up { display: none; }
  .places { grid-template-columns: 1fr; height: auto; }
  .map-box { height: 240px; }
  .inner { padding: 20px 16px 48px; }
  .banner { min-height: 360px; }
  /* 좁은 화면에선 사진을 더 옅게 깔아 글자가 먼저 보이게 */
  .scene { object-position: 62% 45%; }
  .shade { background: linear-gradient(180deg, rgba(250, 250, 250, 0) 38%, var(--bg) 100%), linear-gradient(90deg, rgba(255, 255, 255, .95) 0%, rgba(255, 255, 255, .75) 60%, rgba(255, 255, 255, .3) 100%); }
  .hero-text { padding: 40px 16px 80px; }
  .tag-line { font-size: 21px; }
  .hero h1 { font-size: 44px; }
  .sub { font-size: 14.5px; }
  .linkbar { margin-top: -30px; padding: 0 10px; }
}
</style>
