<template>
  <div v-if="cat" class="catpage">
    <header class="card banner">
      <div class="art"><CategoryArt :kind="cat.key" fill /></div>
      <div>
        <span class="tag" :class="`tone-${cat.tone}`">카테고리</span>
        <h1>{{ cat.label }}</h1>
        <p>{{ cat.desc }}</p>
      </div>
    </header>

    <LinkBar :category="cat.key" />

    <section class="card block">
      <h2 class="section-title">저장한 항목 <small>{{ items.length }}개</small></h2>
      <div class="cards">
        <div v-for="i in items" :key="i.id" class="cell">
          <EventCard :item="i" />
          <div class="acts">
            <select :value="cat.key" aria-label="카테고리 이동" @change="move(i, $event.target.value)">
              <option v-for="c in CATEGORIES" :key="c.key" :value="c.key">{{ c.key === cat.key ? '다른 카테고리로 이동…' : c.label }}</option>
            </select>
            <button class="text" @click="remove(i)">삭제</button>
          </div>
        </div>
      </div>
      <p v-if="!items.length && loaded" class="empty">아직 '{{ cat.label }}'에 저장한 항목이 없어요. 위에 링크를 넣고 확인하면 여기에 모여요.</p>
      <p v-if="error" class="err">{{ error }}</p>
    </section>

    <nav class="others">
      <span class="muted">다른 카테고리</span>
      <RouterLink v-for="c in CATEGORIES.filter(x => x.key !== cat.key)" :key="c.key" :to="`/category/${c.key}`" class="tag" :class="`tone-${c.tone}`">{{ c.label }}</RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getItems, patchItem, deleteItem } from '../api/nexto'
import { CATEGORIES, CATEGORY } from '../utils/labels'
import { fromItem } from '../utils/events'
import CategoryArt from '../components/CategoryArt.vue'
import LinkBar from '../components/LinkBar.vue'
import EventCard from '../components/EventCard.vue'

const route = useRoute(), router = useRouter()
const cat = computed(() => CATEGORY[route.params.key])
const items = ref([]), loaded = ref(false), error = ref('')

async function move(i, to) {
  if (to === cat.value.key) return
  try { await patchItem(i.id, { category: to }); items.value = items.value.filter(x => x.id !== i.id) } catch (e) { error.value = e.message }
}
async function remove(i) {
  if (!confirm(`'${i.title}'을(를) 삭제할까요? 캘린더에서도 사라져요.`)) return
  try { await deleteItem(i.id); items.value = items.value.filter(x => x.id !== i.id) } catch (e) { error.value = e.message }
}
onMounted(async () => {
  if (!cat.value) return router.replace('/items')
  items.value = (await getItems({ category: cat.value.key })).map(fromItem); loaded.value = true
})
</script>

<style scoped>
.catpage { display: grid; gap: 20px; }
.banner { display: flex; align-items: center; gap: 22px; margin: 0; padding: 16px; }
.art { flex: none; width: 200px; aspect-ratio: 5 / 3; border-radius: 12px; overflow: hidden; }
.art :deep(svg) { width: 100%; height: 100%; display: block; }
.banner h1 { margin: 6px 0 2px; font-size: 28px; }
.banner p { margin: 0; color: var(--muted); }
.block { margin: 0; padding: 22px 24px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.cell { display: grid; gap: 6px; }
.acts { display: flex; gap: 6px; align-items: center; }
.acts select { flex: 1; padding: 5px 8px; font-size: 13px; color: var(--muted); }
.acts button { font-size: 13px; }
.err { color: var(--i-red); font-size: 13px; }
.others { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 13px; }
.others a { text-decoration: none; }
.muted { color: var(--muted); margin-right: 4px; }
@media (max-width: 640px) { .banner { flex-direction: column; align-items: flex-start; } .art { width: 100%; } }
</style>
