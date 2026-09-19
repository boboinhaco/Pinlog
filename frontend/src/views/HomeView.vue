<template>
  <div>
    <CoverHeader :title="title" subtitle="SNS에서 본 좋은 정보를, 확인된 다음 일정으로" :cover="auth.user?.cover"
                 :editable="!!auth.user && !auth.isDemo" @change="c => auth.update({ cover: c ?? '' })" />

    <div class="page">
      <LinkBar id="link" :notice="addedNotice" />

      <div class="main">
        <ArchProfile />

        <div class="right">
          <!-- 9개 카테고리 블록 -->
          <section>
            <div class="section-title">
              <span>My Notebook</span>
              <div class="tools">
                <input v-if="searching" ref="searchEl" v-model="query" class="search" placeholder="카테고리 검색" @blur="!query && (searching = false)" />
                <button v-else class="text" aria-label="카테고리 검색" @click="openSearch">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
                </button>
                <button class="new" @click="focusLink">New</button>
              </div>
            </div>
            <div class="gallery">
              <RouterLink v-for="c in shownCategories" :key="c.key" :to="`/category/${c.key}`" class="block">
                <div class="art"><CategoryArt :kind="c.key" /></div>
                <div class="label">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 3h9l4 4v14H6z" /><path d="M14 3v5h5" /></svg>
                  <span>{{ c.label }}</span>
                  <small>{{ counts[c.key] || 0 }}</small>
                </div>
              </RouterLink>
            </div>
            <p v-if="!shownCategories.length" class="empty">'{{ query }}'에 맞는 카테고리가 없어요.</p>
          </section>

          <QuickNotes />
        </div>
      </div>

      <!-- 캘린더 -->
      <section class="block-section">
        <h2 class="section-title deco"><span>˚❀⋆.ೃ࿔*:･ Calendar ˚❀⋆.ೃ࿔*:･</span>
          <RouterLink to="/calendar" class="more-link">전체 보기</RouterLink></h2>
        <NotionCalendar v-model:month="month" :events="calEvents" />
      </section>

      <!-- 지도 -->
      <section class="block-section">
        <h2 class="section-title"><span>📍 저장된 장소</span><small>{{ places.length }}곳</small></h2>
        <div class="places">
          <PlaceMap :places="places" height="320px" expand-to="/map" />
          <div class="place-list">
            <RouterLink v-for="p in places" :key="p.name" :to="`/items/${p.items[0].item_id}`" class="place">
              <strong class="serif">{{ p.name }}</strong>
              <small>{{ p.address || '주소 미상' }}</small>
              <span class="evidence">{{ p.items.map(i => i.title).join(', ') }}</span>
            </RouterLink>
            <p v-if="!places.length" class="empty">장소가 있는 일정을 저장하면 지도에 모여요.</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCalendar, getPlaces, getItems } from '../api/nexto'
import { useAuthStore } from '../stores/auth'
import { CATEGORIES } from '../utils/labels'
import { fromCalendar, mergeById, monthRange } from '../utils/events'
import CoverHeader from '../components/CoverHeader.vue'
import LinkBar from '../components/LinkBar.vue'
import ArchProfile from '../components/ArchProfile.vue'
import CategoryArt from '../components/CategoryArt.vue'
import QuickNotes from '../components/QuickNotes.vue'
import NotionCalendar from '../components/NotionCalendar.vue'
import PlaceMap from '../components/PlaceMap.vue'

const auth = useAuthStore(), route = useRoute(), router = useRouter()
const month = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const calEvents = ref([]), places = ref([]), counts = ref({}), addedNotice = ref('')
const searching = ref(false), query = ref(''), searchEl = ref(null)

const title = computed(() => auth.user && !auth.isDemo ? `${auth.displayName}의 NEXTO` : 'NEXTO')
const shownCategories = computed(() => CATEGORIES.filter(c => !query.value || (c.label + c.desc).includes(query.value.trim())))

const openSearch = async () => { searching.value = true; await nextTick(); searchEl.value?.focus() }
const focusLink = () => { const el = document.querySelector('#link input'); el?.scrollIntoView({ behavior: 'smooth', block: 'center' }); el?.focus() }

async function loadMonth() { calEvents.value = mergeById((await getCalendar(...monthRange(month.value))).map(fromCalendar)) }
async function loadCounts() {
  counts.value = (await getItems()).reduce((acc, i) => ({ ...acc, [i.category ?? 'OTHER']: (acc[i.category ?? 'OTHER'] ?? 0) + 1 }), {})
}

watch(month, loadMonth)
onMounted(async () => {
  // 검토 화면에서 저장하고 돌아오면 알림 + 해당 달로 이동
  if (route.query.added) {
    addedNotice.value = `${route.query.added}건을 캘린더에 추가했어요.`
    if (route.query.month) month.value = new Date(route.query.month + '-01T00:00')
    router.replace({ query: {} })
  }
  await Promise.all([loadMonth(), getPlaces().then(p => (places.value = p)), loadCounts()])
})
</script>

<style scoped>
.page { padding-top: 8px; }
.main { display: grid; grid-template-columns: 250px 1fr; gap: 36px; margin-top: 36px; align-items: start; }
.right { display: grid; gap: 24px; min-width: 0; }
.tools { display: flex; align-items: center; gap: 4px; font-family: var(--sans); }
.search { width: 160px; padding: 4px 8px; font-size: 13px; }
.new { padding: 3px 12px; font-size: 13px; }
.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.block { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; text-decoration: none; background: #fff; transition: box-shadow .15s; }
.block:hover { box-shadow: 0 2px 10px rgba(15, 15, 15, .08); }
.art { aspect-ratio: 5 / 3; border-bottom: 1px solid var(--line); }
.art :deep(svg) { width: 100%; height: 100%; display: block; }
.label { display: flex; align-items: center; gap: 6px; padding: 8px 10px; font-family: var(--serif); font-size: 14px; color: var(--ink); }
.label svg { color: var(--faint); flex: none; }
.label span { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.label small { font-family: var(--sans); font-size: 12px; color: var(--faint); }
.block-section { margin-top: 56px; }
.deco span { letter-spacing: .02em; }
.more-link { font-family: var(--sans); font-size: 13px; font-weight: 400; color: var(--faint); text-decoration: none; }
.more-link:hover { color: var(--ink); }
.places { display: grid; grid-template-columns: 1.6fr 1fr; gap: 16px; }
.place-list { display: grid; align-content: start; max-height: 320px; overflow-y: auto; border: 1px solid var(--line); border-radius: 8px; }
.place { display: grid; gap: 2px; padding: 12px 14px; border-bottom: 1px solid var(--line); text-decoration: none; }
.place:last-child { border-bottom: 0; }
.place:hover { background: var(--soft); }
.place strong { font-size: 14.5px; }
.place small { font-size: 13px; color: var(--muted); }
@media (max-width: 900px) {
  .main { grid-template-columns: 1fr; }
  .main > :first-child { max-width: 340px; width: 100%; margin: 0 auto; }
  .main > :first-child :deep(.arch) { max-width: 200px; width: 100%; margin: 0 auto; }
  .places { grid-template-columns: 1fr; }
}
@media (max-width: 560px) { .gallery { grid-template-columns: repeat(2, 1fr); } }
</style>
