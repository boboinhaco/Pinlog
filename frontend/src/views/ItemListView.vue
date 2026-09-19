<template>
  <section>
    <h1 class="page-title">저장됨 <small>{{ items.length }}개</small></h1>
    <div class="filters">
      <button class="tag" :class="filter ? 'tone-gray off' : 'tone-gray'" @click="filter = ''">전체</button>
      <button v-for="c in CATEGORIES" :key="c.key" class="tag" :class="[`tone-${c.tone}`, { off: filter && filter !== c.key }]" @click="filter = filter === c.key ? '' : c.key">
        {{ c.label }} {{ counts[c.key] ?? 0 }}
      </button>
    </div>
    <div v-for="g in groups" :key="g.key" class="group">
      <h2 class="section-title"><RouterLink :to="`/category/${g.key}`">{{ g.label }}</RouterLink><small>{{ g.items.length }}개</small></h2>
      <div class="table">
        <RouterLink v-for="i in g.items" :key="i.id" :to="`/items/${i.id}`" class="tr">
          <span class="name serif">{{ i.title }}</span>
          <span class="muted">{{ periodLabel(i.start, i.end) }}</span>
          <span class="muted">{{ i.place?.name ?? '' }}</span>
          <span><i class="tag" :class="`tone-${GRADE[i.grade]?.tone ?? 'gray'}`">{{ GRADE[i.grade]?.label ?? '-' }}</i></span>
        </RouterLink>
      </div>
    </div>
    <p v-if="loaded && !items.length" class="empty">아직 저장한 항목이 없어요. 홈에서 SNS 링크를 넣어보세요.</p>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getItems } from '../api/nexto'
import { CATEGORIES, GRADE } from '../utils/labels'
import { periodLabel, fromItem } from '../utils/events'

const items = ref([]), filter = ref(''), loaded = ref(false)
const counts = computed(() => items.value.reduce((a, i) => ({ ...a, [i.category]: (a[i.category] ?? 0) + 1 }), {}))
const groups = computed(() => CATEGORIES.filter(c => !filter.value || c.key === filter.value)
  .map(c => ({ ...c, items: items.value.filter(i => (i.category ?? 'OTHER') === c.key) })).filter(g => g.items.length))
onMounted(async () => { items.value = (await getItems()).map(fromItem); loaded.value = true })
</script>

<style scoped>
.page-title small { font-family: var(--sans); font-size: 15px; font-weight: 400; color: var(--faint); margin-left: 6px; }
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.filters .tag { border: 0; padding: 3px 9px; font-size: 13px; cursor: pointer; }
.filters .tag.off { opacity: .45; }
.group { margin-top: 28px; }
.group .section-title { font-size: 17px; }
.group .section-title a { text-decoration: none; }
.table { border-top: 1px solid var(--line); }
.tr { display: grid; grid-template-columns: 2fr 1fr 1fr .8fr; gap: 12px; align-items: center; padding: 9px 4px; border-bottom: 1px solid var(--line); text-decoration: none; font-size: 14px; }
.tr:hover { background: var(--soft); }
.name { font-weight: 600; }
.muted { color: var(--muted); }
i.tag { font-style: normal; }
@media (max-width: 640px) { .tr { grid-template-columns: 1fr auto; } .tr > span:nth-child(2), .tr > span:nth-child(3) { font-size: 12.5px; } }
</style>
