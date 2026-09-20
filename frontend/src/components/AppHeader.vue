<template>
  <header class="hdr">
    <RouterLink to="/home" class="brand" aria-label="Pinlog 홈"><PinLogo :size="32" /></RouterLink>
    <nav class="tabs">
      <RouterLink to="/home">홈</RouterLink>
      <RouterLink to="/calendar">내 일정</RouterLink>
      <RouterLink to="/map">저장한 장소</RouterLink>
      <RouterLink to="/liked">좋아요</RouterLink>
    </nav>

    <div ref="root" class="right">
      <!-- 검색: 저장한 항목 제목·장소 -->
      <div class="pop-wrap">
        <button class="icon" :class="{ on: open === 'search' }" aria-label="저장한 항목 검색" @click="toggle('search')"><Search :size="22" :stroke-width="1.9" /></button>
        <div v-if="open === 'search'" class="pop">
          <label class="sbox"><Search :size="16" /><input ref="searchEl" v-model="q" placeholder="저장한 일정·장소 검색" /></label>
          <RouterLink v-for="i in results" :key="i.id" :to="`/items/${i.id}`" class="row" @click="open = ''">
            <span class="thumb" :class="`tone-${CATEGORY[i.category]?.tone ?? 'gray'}`"><CalendarDays :size="16" /></span>
            <span><b>{{ i.title }}</b><small>{{ periodLabel(i.start, i.end) }}<template v-if="i.place"> · {{ i.place.name }}</template></small></span>
          </RouterLink>
          <p v-if="q && !results.length" class="none">'{{ q }}'에 맞는 항목이 없어요.</p>
        </div>
      </div>

      <!-- 알림: 7일 안에 시작·마감되는 일정 -->
      <div class="pop-wrap">
        <button class="icon" :class="{ on: open === 'bell' }" aria-label="다가오는 일정 알림" @click="toggle('bell')">
          <Bell :size="22" :stroke-width="1.9" /><i v-if="upcoming.length" class="dot">{{ upcoming.length }}</i>
        </button>
        <div v-if="open === 'bell'" class="pop">
          <p class="pop-title">다가오는 일정</p>
          <RouterLink v-for="u in upcoming" :key="u.id" :to="`/items/${u.id}`" class="row" @click="open = ''">
            <span class="thumb" :class="`tone-${CATEGORY[u.category]?.tone ?? 'gray'}`"><Clock :size="16" /></span>
            <span><b>{{ u.title }}</b><small>{{ u.label }}</small></span>
          </RouterLink>
          <p v-if="!upcoming.length" class="none">7일 안에 다가오는 일정이 없어요.</p>
        </div>
      </div>

      <UserMenu :open="open === 'user'" @toggle="toggle('user')" @close="open = ''" />
    </div>
  </header>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Bell, CalendarDays, Clock } from 'lucide-vue-next'
import { getItems } from '../api/nexto'
import { fromItem, periodLabel, ymd } from '../utils/events'
import { CATEGORY } from '../utils/labels'
import PinLogo from './PinLogo.vue'
import UserMenu from './UserMenu.vue'

const route = useRoute()
const open = ref(''), q = ref(''), items = ref([]), root = ref(null), searchEl = ref(null)
const load = async () => { items.value = (await getItems().catch(() => [])).map(fromItem) }

async function toggle(name) {
  open.value = open.value === name ? '' : name
  if (open.value === 'search') { await nextTick(); searchEl.value?.focus() }
}
const results = computed(() => {
  const k = q.value.trim()
  return k ? items.value.filter(i => (i.title + (i.place?.name ?? '')).includes(k)).slice(0, 8) : items.value.slice(0, 5)
})
// 시작일 또는 마감일이 오늘~7일 안
const upcoming = computed(() => {
  const today = ymd(new Date()), week = ymd(new Date(Date.now() + 7 * 86400000))
  return items.value.flatMap(i => {
    if (i.start && i.start >= today && i.start <= week) return [{ ...i, label: `${diff(i.start)} 시작 · ${periodLabel(i.start, i.end)}`, key: i.start }]
    if (i.end && i.end >= today && i.end <= week) return [{ ...i, label: `${diff(i.end)} 마감 · ${periodLabel(i.start, i.end)}`, key: i.end }]
    return []
  }).sort((a, b) => a.key.localeCompare(b.key))
})
const diff = d => { const n = Math.round((new Date(d + 'T00:00') - new Date(ymd(new Date()) + 'T00:00')) / 86400000); return n === 0 ? '오늘' : `D-${n}` }

// 바깥 클릭 시 닫기
const onDoc = e => { if (root.value && !root.value.contains(e.target)) open.value = '' }
onMounted(() => { document.addEventListener('click', onDoc); load() })
watch(() => route.fullPath, () => { open.value = ''; load() })
onBeforeUnmount(() => document.removeEventListener('click', onDoc))
</script>

<style scoped>
.hdr { position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; gap: 36px; height: 68px; padding: 0 28px 0 32px; background: rgba(255, 255, 255, .86); backdrop-filter: saturate(180%) blur(16px); border-bottom: 1px solid var(--line); }
.brand { text-decoration: none; }
.tabs { display: flex; gap: 4px; }
.tabs a { position: relative; padding: 8px 14px; border-radius: 10px; text-decoration: none; color: var(--muted); font-weight: 600; white-space: nowrap; transition: color .15s, background .15s; }
.tabs a:hover { color: var(--ink); background: var(--hover); }
.tabs a.router-link-active { color: var(--ink); }
.tabs a.router-link-active::after { content: ''; position: absolute; left: 14px; right: 14px; bottom: -14px; height: 2.5px; border-radius: 2px; background: var(--cta); }
.right { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.pop-wrap { position: relative; }
.icon { position: relative; display: grid; place-items: center; width: 42px; height: 42px; padding: 0; border-radius: 12px; background: none; color: var(--ink); }
.icon:hover, .icon.on { background: var(--hover); }
.dot { position: absolute; top: 4px; right: 3px; min-width: 17px; height: 17px; padding: 0 4px; border-radius: 9px; background: #ff3040; color: #fff; font-size: 10.5px; font-style: normal; font-weight: 700; line-height: 17px; border: 2px solid #fff; box-sizing: content-box; }
.pop { position: absolute; right: 0; top: 52px; width: 320px; padding: 8px; background: #fff; border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow-lg); }
.sbox { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; padding: 0 12px; border-radius: 12px; background: var(--hover); color: var(--muted); }
.sbox input { border: 0; background: none; padding: 10px 0; box-shadow: none; }
.pop-title { margin: 8px 10px; font-weight: 700; font-size: 15px; }
.row { display: flex; align-items: center; gap: 12px; padding: 8px 10px; border-radius: 12px; text-decoration: none; }
.row:hover { background: var(--hover); }
.thumb { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 12px; flex: none; }
.row > span:last-child { display: grid; min-width: 0; }
.row b { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row small { font-size: 12.5px; color: var(--muted); }
.none { margin: 10px; font-size: 13px; color: var(--faint); }
@media (max-width: 760px) {
  .hdr { gap: 10px; padding: 0 12px; height: 60px; }
  .brand :deep(b) { display: none; }
  .tabs a { padding: 8px 8px; font-size: 14px; }
  .tabs a.router-link-active::after { bottom: -10px; left: 8px; right: 8px; }
  .right { gap: 0; }
  .right > .pop-wrap:first-child { display: none; }
  .pop { position: fixed; left: 12px; right: 12px; top: 64px; width: auto; }
}
</style>
