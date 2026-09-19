<template>
  <div v-if="cat">
    <CoverHeader :title="cat.label" :subtitle="cat.desc" height="200px">
      <template #art><CategoryArt :kind="cat.key" fill /></template>
    </CoverHeader>

    <div class="page">
      <LinkBar :category="cat.key" />

      <section class="list">
        <h2 class="section-title"><span>저장한 항목</span><small>{{ items.length }}개</small></h2>
        <div class="table">
          <div class="tr th"><span>이름</span><span>기간 · 마감</span><span>장소</span><span>확인</span><span></span></div>
          <div v-for="i in items" :key="i.id" class="tr">
            <RouterLink :to="`/items/${i.id}`" class="name serif">{{ i.title }}</RouterLink>
            <span class="muted">{{ periodLabel(i.start, i.end) }}</span>
            <span class="muted">{{ i.place?.name ?? '-' }}</span>
            <span><i class="tag" :class="`tone-${GRADE[i.grade]?.tone ?? 'gray'}`">{{ GRADE[i.grade]?.label ?? '-' }}</i></span>
            <span class="acts">
              <select :value="cat.key" aria-label="카테고리 이동" @change="move(i, $event.target.value)">
                <option v-for="c in CATEGORIES" :key="c.key" :value="c.key">{{ c.key === cat.key ? '이동…' : c.label }}</option>
              </select>
              <button class="text" aria-label="삭제" @click="remove(i)">삭제</button>
            </span>
          </div>
          <p v-if="!items.length && loaded" class="empty">아직 '{{ cat.label }}'에 저장한 항목이 없어요.<br>위에 링크를 넣고 확인하면 여기에 모여요.</p>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
      </section>

      <nav class="others">
        <span class="muted">다른 카테고리</span>
        <RouterLink v-for="c in CATEGORIES.filter(x => x.key !== cat.key)" :key="c.key" :to="`/category/${c.key}`" class="tag" :class="`tone-${c.tone}`">{{ c.label }}</RouterLink>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getItems, patchItem, deleteItem } from '../api/nexto'
import { CATEGORIES, CATEGORY, GRADE } from '../utils/labels'
import { periodLabel, fromItem } from '../utils/events'
import CoverHeader from '../components/CoverHeader.vue'
import CategoryArt from '../components/CategoryArt.vue'
import LinkBar from '../components/LinkBar.vue'

const route = useRoute(), router = useRouter()
const cat = computed(() => CATEGORY[route.params.key])
const items = ref([]), loaded = ref(false), error = ref('')

async function load() {
  items.value = (await getItems({ category: cat.value.key })).map(fromItem); loaded.value = true
}
async function move(i, to) {
  if (to === cat.value.key) return
  try { await patchItem(i.id, { category: to }); items.value = items.value.filter(x => x.id !== i.id) } catch (e) { error.value = e.message }
}
async function remove(i) {
  if (!confirm(`'${i.title}'을(를) 삭제할까요? 캘린더에서도 사라져요.`)) return
  try { await deleteItem(i.id); items.value = items.value.filter(x => x.id !== i.id) } catch (e) { error.value = e.message }
}
onMounted(() => (cat.value ? load() : router.replace('/home')))
</script>

<style scoped>
.list { margin-top: 36px; }
.table { border-top: 1px solid var(--line); }
.tr { display: grid; grid-template-columns: 2fr 1.1fr 1.1fr .9fr auto; gap: 12px; align-items: center; padding: 9px 4px; border-bottom: 1px solid var(--line); font-size: 14px; }
.th { color: var(--faint); font-size: 13px; }
.name { text-decoration: none; font-weight: 600; }
.name:hover { text-decoration: underline; }
.muted { color: var(--muted); }
.acts { display: flex; gap: 4px; align-items: center; }
.acts select { width: auto; padding: 3px 6px; font-size: 12.5px; color: var(--muted); }
.acts button { font-size: 13px; }
i.tag { font-style: normal; }
.err { color: var(--i-red); font-size: 13px; }
.others { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 40px; font-size: 13px; }
.others a { text-decoration: none; }
@media (max-width: 760px) {
  .th { display: none; }
  .tr { grid-template-columns: 1fr auto; gap: 4px 8px; }
  .tr > span:nth-child(2), .tr > span:nth-child(3) { font-size: 13px; }
  .acts { grid-column: 1 / -1; }
}
</style>
