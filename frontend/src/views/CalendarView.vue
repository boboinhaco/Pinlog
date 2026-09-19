<template>
  <section>
    <h1 class="page-title">˚❀⋆.ೃ࿔*:･ Calendar</h1>
    <NotionCalendar v-model:month="month" :events="events" :max-lanes="4" />
    <h2 class="section-title list-title">{{ month.getMonth() + 1 }}월 일정 <small>{{ events.length }}건</small></h2>
    <div class="table">
      <RouterLink v-for="e in events" :key="e.id" :to="`/items/${e.id}`" class="tr">
        <span class="name serif">{{ e.title }}</span>
        <span class="muted">{{ periodLabel(e.start, e.end) }}</span>
        <span><i class="tag" :class="`tone-${CATEGORY[e.category]?.tone ?? 'gray'}`">{{ CATEGORY[e.category]?.label ?? '기타' }}</i></span>
        <span class="muted">{{ e.place?.name ?? '' }}</span>
      </RouterLink>
      <p v-if="!events.length" class="empty">이 달에는 일정이 없어요.</p>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getCalendar } from '../api/nexto'
import { CATEGORY } from '../utils/labels'
import { periodLabel, fromCalendar, mergeById, monthRange } from '../utils/events'
import NotionCalendar from '../components/NotionCalendar.vue'

const month = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1)), events = ref([])
watch(month, async m => { events.value = mergeById((await getCalendar(...monthRange(m))).map(fromCalendar)) }, { immediate: true })
</script>

<style scoped>
.list-title { margin-top: 36px; font-size: 17px; }
.table { border-top: 1px solid var(--line); }
.tr { display: grid; grid-template-columns: 2fr 1fr .9fr 1fr; gap: 12px; align-items: center; padding: 9px 4px; border-bottom: 1px solid var(--line); text-decoration: none; font-size: 14px; }
.tr:hover { background: var(--soft); }
.name { font-weight: 600; }
.muted { color: var(--muted); }
i.tag { font-style: normal; }
@media (max-width: 640px) { .tr { grid-template-columns: 1fr auto; } }
</style>
