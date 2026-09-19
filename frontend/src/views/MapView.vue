<template>
  <section>
    <h1 class="page-title">📍 지도</h1>
    <div class="layout">
      <PlaceMap :places="places" height="min(70vh, 560px)" class="map" />
      <div class="list">
        <h2 class="section-title">저장된 장소 <small>{{ places.length }}곳</small></h2>
        <div v-for="p in places" :key="p.name" class="place">
          <strong class="serif">{{ p.name }}</strong>
          <small>{{ p.address || '주소 미상' }}</small>
          <RouterLink v-for="it in p.items" :key="it.item_id" :to="`/items/${it.item_id}`" class="link">
            {{ it.title }} · {{ periodLabel(it.event_period?.start, it.event_period?.end) }}
          </RouterLink>
        </div>
        <p v-if="!places.length" class="empty">장소가 있는 일정을 저장하면 여기에 모여요.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPlaces } from '../api/nexto'
import { periodLabel } from '../utils/events'
import PlaceMap from '../components/PlaceMap.vue'

const places = ref([])
onMounted(async () => (places.value = await getPlaces()))
</script>

<style scoped>
.layout { display: grid; grid-template-columns: 1.7fr 1fr; gap: 20px; align-items: start; }
.map { border: 1px solid var(--line); }
.section-title { font-size: 17px; }
.place { display: grid; gap: 2px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.place:last-of-type { border-bottom: 0; }
.place small { color: var(--muted); margin-bottom: 4px; }
.link { font-size: 14px; color: var(--blue); text-decoration: none; }
.link:hover { text-decoration: underline; }
@media (max-width: 860px) { .layout { grid-template-columns: 1fr; } }
</style>
