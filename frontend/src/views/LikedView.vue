<template>
  <div class="liked">
    <PageHero tagline="좋아하는 것들이 모여, 더 특별한 하루가 돼요." title="좋아요한 콘텐츠" sub="SNS에서 저장한 콘텐츠를 모아보고, 손쉽게 일정이나 장소로 변환해보세요."
              doodle="마음에 드는 콘텐츠를<br>일정으로 만들어<br>특별한 하루를 계획해보세요!" />
    <LinkBar button-label="콘텐츠 추가하기" :query="{ liked: '1' }" class="lb" />

    <div class="card filters">
      <div class="grp"><b>SNS 출처</b>
        <button :class="{ on: !src }" @click="src = ''">전체</button>
        <button v-for="s in presentSources" :key="s.key" :class="{ on: src === s.key }" @click="src = s.key"><i :style="{ background: s.color }"></i>{{ s.label }}</button>
      </div>
      <div class="grp"><b>콘텐츠 유형</b>
        <button :class="{ on: !cat }" @click="cat = ''">전체</button>
        <button v-for="c in presentCats" :key="c.key" :class="{ on: cat === c.key }" @click="cat = c.key">{{ c.label }}</button>
      </div>
      <select v-model="sort" aria-label="정렬"><option value="recent">최근 저장순</option><option value="date">일정 날짜순</option></select>
    </div>

    <p class="count">총 <b>{{ shown.length }}개</b>의 콘텐츠가 저장되어 있어요!</p>

    <div class="layout">
      <div class="grid">
        <article v-for="i in shown" :key="i.id" class="lc" :class="{ on: picked?.id === i.id }" @click="picked = i">
          <div class="img">
            <img v-if="i.image" :src="i.image" alt="" referrerpolicy="no-referrer" @error="i.image = null" />
            <CategoryArt v-else :kind="i.category" fill />
            <span class="src"><i :style="{ background: sourceOf(i.sourceUrl).color }"></i>{{ sourceOf(i.sourceUrl).label }}</span>
            <button class="heart" aria-label="좋아요 취소" @click.stop="unlike(i)"><Heart :size="18" fill="currentColor" /></button>
          </div>
          <div class="body">
            <b>{{ i.title }}</b>
            <p>{{ i.summary || '요약이 없는 콘텐츠예요.' }}</p>
            <div class="meta">
              <span><CalendarDays :size="13" />{{ i.start ? periodLabel(i.start, i.end) : '날짜 없음' }}</span>
              <span v-if="i.place"><MapPin :size="13" />{{ shortPlace(i.place) }}</span>
            </div>
            <div class="acts">
              <button class="ghost" @click.stop="editor = { mode: 'date', item: i }"><CalendarPlus :size="14" />{{ i.start ? '일정 수정' : '일정 추가' }}</button>
              <button v-if="i.place" class="ghost" @click.stop="router.push('/map')"><MapPinned :size="14" />지도에서 보기</button>
              <button v-else class="ghost" @click.stop="editor = { mode: 'place', item: i }"><MapPin :size="14" />장소 저장</button>
            </div>
          </div>
        </article>
        <p v-if="loaded && !shown.length" class="empty">{{ items.length ? '조건에 맞는 콘텐츠가 없어요.' : '아직 좋아요한 콘텐츠가 없어요. 위에 링크를 넣거나, 카드의 하트를 눌러 모아보세요.' }}</p>
      </div>

      <!-- AI 콘텐츠 요약 -->
      <aside class="card ai">
        <div class="ai-hd"><b><Sparkles :size="17" />AI 콘텐츠 요약</b><button v-if="picked" class="text" aria-label="요약 닫기" @click="picked = null"><X :size="16" /></button></div>
        <template v-if="picked">
          <span class="tag" :class="`tone-${GRADE[picked.grade]?.tone ?? 'gray'}`">{{ GRADE[picked.grade]?.label ?? '공식 미확인' }}</span>
          <h3>{{ picked.title }}</h3>
          <p v-if="picked.summary" class="sum">{{ picked.summary }}</p>
          <p v-if="picked.officialSummary" class="sum off"><small>공식 공고 기준</small>{{ picked.officialSummary }}</p>
          <ul class="facts">
            <li><CalendarDays :size="15" />{{ picked.start ? periodLong(picked.start, picked.end) : '날짜 정보 없음' }}</li>
            <li><MapPin :size="15" />{{ picked.place ? (picked.place.address || picked.place.name) : '장소 정보 없음' }}</li>
            <li v-for="k in picked.keyPoints.slice(0, 4)" :key="k"><Dot :size="15" />{{ k }}</li>
          </ul>
          <RouterLink :to="`/items/${picked.id}`" class="detail">자세히 보기 →</RouterLink>
        </template>
        <template v-else>
          <p class="hint">콘텐츠를 선택하면,<br>{{ BRAND }} AI가 핵심 정보를 정리해드려요.</p>
          <div class="illo" aria-hidden="true">
            <div class="doc"><span class="av"></span><span class="ln"></span><span class="ln s"></span><span class="ln"></span></div>
            <svg class="cursor" width="34" height="34" viewBox="0 0 24 24" fill="#fff" stroke="#2f4fa8" stroke-width="1.6"><path d="M5 3l13 8-6 1.5L9 19z" /></svg>
          </div>
          <ul class="feats">
            <li><MapPin :size="15" />장소명과 위치 정보 추출</li><li><CalendarDays :size="15" />날짜 및 기간 인식</li>
            <li><FileText :size="15" />주요 내용 요약</li><li><ShieldCheck :size="15" />공식 공고와 비교 후 저장</li>
          </ul>
          <p class="hand foot">좋아하는 콘텐츠가<br>특별한 일정이 되는 순간</p>
        </template>
      </aside>
    </div>

    <ItemEditor v-if="editor" :mode="editor.mode" :item="editor.item" @close="editor = null" @saved="onSaved" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Heart, CalendarDays, CalendarPlus, MapPin, MapPinned, Sparkles, X, Dot, FileText, ShieldCheck } from 'lucide-vue-next'
import { getItems, patchItem } from '../api/nexto'
import { CATEGORIES, GRADE } from '../utils/labels'
import { fromItem, periodLabel, periodLong } from '../utils/events'
import { SOURCES, sourceOf } from '../utils/source'
import { BRAND } from '../utils/brand'
import PageHero from '../components/PageHero.vue'
import LinkBar from '../components/LinkBar.vue'
import CategoryArt from '../components/CategoryArt.vue'
import ItemEditor from '../components/ItemEditor.vue'

const router = useRouter()
const items = ref([]), loaded = ref(false), src = ref(''), cat = ref(''), sort = ref('recent'), picked = ref(null), editor = ref(null)

const presentSources = computed(() => SOURCES.filter(s => items.value.some(i => sourceOf(i.sourceUrl).key === s.key)))
const presentCats = computed(() => CATEGORIES.filter(c => items.value.some(i => i.category === c.key)))
const shown = computed(() => items.value
  .filter(i => (!src.value || sourceOf(i.sourceUrl).key === src.value) && (!cat.value || i.category === cat.value))
  .sort((a, b) => sort.value === 'date' ? (a.start ?? '9').localeCompare(b.start ?? '9') : (b.created ?? '').localeCompare(a.created ?? '')))
const shortPlace = p => (p.address ?? p.name).split(/\s+/).slice(0, 2).join(' ')

async function load() { items.value = (await getItems()).map(fromItem).filter(i => i.liked); loaded.value = true }
async function unlike(i) {
  await patchItem(i.id, { fields: { liked: false } })
  items.value = items.value.filter(x => x.id !== i.id)
  if (picked.value?.id === i.id) picked.value = null
}
async function onSaved(saved) {
  editor.value = null
  const fresh = fromItem(saved)
  items.value = items.value.map(i => (i.id === fresh.id ? fresh : i))
  if (picked.value?.id === fresh.id) picked.value = fresh
}
onMounted(load)
</script>

<style scoped>
.liked { display: grid; gap: 16px; }
.lb { max-width: 900px; width: 100%; margin: 0 auto; }
.filters { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 24px; margin: 0; padding: 12px 16px; }
.grp { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.grp b { margin-right: 6px; font-size: 14px; }
.grp button { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 999px; background: #fff; color: var(--ink-2); border: 1px solid var(--line); font-size: 13px; font-weight: 500; }
.grp button.on { background: var(--cta); color: #fff; border-color: transparent; }
.grp i { width: 12px; height: 12px; border-radius: 4px; }
.filters select { width: auto; margin-left: auto; min-width: 150px; border-radius: 10px; }
.count { margin: 0; font-size: 14px; color: var(--muted); }
.count b { color: var(--ink); }
.layout { display: grid; grid-template-columns: 1fr 280px; gap: 18px; align-items: start; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; }
.lc { display: grid; background: #fff; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; cursor: pointer; box-shadow: var(--shadow); transition: box-shadow .15s; }
.lc:hover { box-shadow: 0 8px 22px rgba(40, 70, 140, .12); }
.lc.on { border-color: var(--accent); box-shadow: 0 0 0 2px var(--focus); }
.img { position: relative; aspect-ratio: 16 / 9; }
.img img, .img :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.src { position: absolute; left: 10px; top: 10px; display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; background: #fff; font-size: 12px; font-weight: 600; box-shadow: 0 1px 4px rgba(0, 0, 0, .1); }
.src i { width: 12px; height: 12px; border-radius: 4px; }
.heart { position: absolute; right: 8px; top: 8px; width: 34px; height: 34px; padding: 0; border-radius: 50%; background: rgba(28, 40, 72, .35); display: grid; place-items: center; }
.body { display: grid; gap: 6px; padding: 12px 14px 14px; }
.body b { font-size: 15px; }
.body p { margin: 0; font-size: 13px; line-height: 1.5; color: var(--muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta { display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 12.5px; color: var(--muted); }
.meta span { display: inline-flex; align-items: center; gap: 4px; }
.acts { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 4px; }
.acts button { display: inline-flex; align-items: center; justify-content: center; gap: 5px; padding: 7px 4px; font-size: 12.5px; color: var(--ink); border-radius: 12px; }
.ai { position: sticky; top: 90px; margin: 0; padding: 18px; display: grid; gap: 10px; }
.ai-hd { display: flex; justify-content: space-between; align-items: center; font-size: 16px; color: var(--ink); }
.ai-hd b { display: inline-flex; align-items: center; gap: 7px; }
.ai-hd .lucide { color: var(--accent); }
.ai h3 { margin: 0; font-size: 17px; }
.sum { margin: 0; font-size: 13.5px; line-height: 1.65; }
.sum.off { padding: 10px 12px; border-radius: 10px; background: var(--soft); }
.sum small { display: block; font-size: 11.5px; color: var(--muted); font-weight: 600; }
.facts, .feats { margin: 0; padding: 0; list-style: none; display: grid; gap: 8px; font-size: 13px; color: var(--ink-2); }
.facts li, .feats li { display: flex; align-items: flex-start; gap: 8px; }
.facts .lucide, .feats .lucide { color: var(--accent); margin-top: 2px; }
.detail { justify-self: start; font-size: 14px; font-weight: 600; color: var(--accent); text-decoration: none; }
.hint { margin: 0; font-size: 13.5px; line-height: 1.6; color: var(--muted); }
.illo { position: relative; height: 130px; display: grid; place-items: center; border-radius: 12px; background: linear-gradient(180deg, var(--accent-soft), #fff); }
.doc { width: 150px; padding: 14px; border-radius: 10px; background: #fff; box-shadow: 0 6px 16px rgba(40, 70, 140, .12); display: grid; grid-template-columns: 34px 1fr; gap: 6px 10px; }
.doc .av { grid-row: span 3; width: 34px; height: 34px; border-radius: 8px; background: var(--tint); }
.doc .ln { height: 7px; border-radius: 4px; background: #dbe5f6; }
.doc .ln.s { width: 60%; }
.cursor { position: absolute; right: 38px; bottom: 16px; }
.foot { margin: 6px 0 0; font-size: 19px; line-height: 1.3; color: var(--hand-ink); }
@media (max-width: 1100px) { .layout { grid-template-columns: 1fr; } .ai { position: static; } }
@media (max-width: 640px) { .filters select { margin-left: 0; width: 100%; } }
</style>
