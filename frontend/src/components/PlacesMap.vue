<template>
  <div class="pm">
    <div ref="el" class="canvas"></div>
    <div class="layer-tog" role="group" aria-label="지도 종류">
      <button :class="{ on: layer === 'map' }" @click="setLayer('map')">지도</button>
      <button :class="{ on: layer === 'sat' }" @click="setLayer('sat')">위성</button>
    </div>
    <div class="zoom">
      <button aria-label="확대" @click="map.zoomIn()"><Plus :size="18" /></button>
      <button aria-label="축소" @click="map.zoomOut()"><Minus :size="18" /></button>
      <button aria-label="모든 장소 보기" @click="fit"><Maximize :size="17" /></button>
    </div>
    <button class="locate" @click="locate"><LocateFixed :size="15" />현재 지역으로 이동</button>
    <p v-if="locError" class="loc-err">{{ locError }}</p>
    <ul v-if="legend.length" class="legend">
      <li v-for="l in legend" :key="l.key"><i :style="{ background: l.color }"></i>{{ l.label }}</li>
    </ul>
    <!-- 선택한 장소 카드 -->
    <RouterLink v-if="sel" :to="`/items/${sel.items[0].id}`" class="pop">
      <span class="th"><img v-if="sel.image" :src="sel.image" alt="" referrerpolicy="no-referrer" /><CategoryArt v-else :kind="sel.category" fill /></span>
      <span><b>{{ sel.name }}</b><small>{{ sel.address || sel.items[0].title }}</small></span><ChevronRight :size="18" class="go" />
    </RouterLink>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Plus, Minus, Maximize, LocateFixed, ChevronRight } from 'lucide-vue-next'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { CATEGORY, pinColor } from '../utils/labels'
import CategoryArt from './CategoryArt.vue'

// places: [{name, lat, lng, category, items[], image}], selected: 장소 이름
const props = defineProps({ places: { type: Array, default: () => [] }, selected: String })
const emit = defineEmits(['select'])
const TILES = {
  map: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png', '&copy; OpenStreetMap'],
  sat: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri']
}
const el = ref(null), layer = ref('map'), locError = ref('')
let map, tiles, group, resize

const pins = computed(() => props.places.filter(p => p.lat != null && p.lng != null))
const color = p => pinColor(p.category)
const legend = computed(() => [...new Set(pins.value.map(p => p.category))].map(k => ({ key: k, label: CATEGORY[k]?.label ?? '기타', color: pinColor(k) })))
const sel = computed(() => pins.value.find(p => p.name === props.selected))

const icon = (p, on) => L.divIcon({
  className: 'pm-pin', iconSize: [30, 38], iconAnchor: [15, 36],
  html: `<svg width="30" height="38" viewBox="0 0 30 38"><path d="M15 1C7.3 1 1 7.1 1 14.7 1 25 15 37 15 37s14-12 14-22.3C29 7.1 22.7 1 15 1z" fill="${color(p)}" stroke="#fff" stroke-width="${on ? 3 : 2}"/><circle cx="15" cy="14.5" r="5" fill="#fff"/></svg>`
})

function draw() {
  group.clearLayers()
  for (const p of pins.value) {
    L.marker([p.lat, p.lng], { icon: icon(p, p.name === props.selected), title: p.name }).on('click', () => emit('select', p.name)).addTo(group)
  }
}
function fit() {
  if (pins.value.length > 1) map.fitBounds(L.latLngBounds(pins.value.map(p => [p.lat, p.lng])), { padding: [60, 60], animate: false })
  else if (pins.value.length === 1) map.setView([pins.value[0].lat, pins.value[0].lng], 14, { animate: false })
}
function setLayer(k) {
  layer.value = k
  tiles?.remove(); tiles = L.tileLayer(TILES[k][0], { maxZoom: 19, attribution: TILES[k][1] }).addTo(map)
}
function locate() {
  locError.value = ''
  if (!navigator.geolocation) { locError.value = '이 브라우저는 위치 기능을 지원하지 않아요.'; return }
  navigator.geolocation.getCurrentPosition(pos => map.setView([pos.coords.latitude, pos.coords.longitude], 14),
    () => (locError.value = '위치 권한이 없어 현재 위치로 이동할 수 없어요.'), { timeout: 8000 })
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: false, scrollWheelZoom: false }).setView([37.54, 127.0], 11)
  setLayer('map')
  group = L.layerGroup().addTo(map)
  draw(); fit()
  resize = new ResizeObserver(() => map?.invalidateSize({ animate: false })); resize.observe(el.value)
})
watch(pins, () => { if (map) { draw(); fit() } })
watch(() => props.selected, name => {
  if (!map) return
  draw()
  const p = pins.value.find(x => x.name === name)
  if (p) map.setView([p.lat, p.lng], Math.max(map.getZoom(), 14), { animate: true })
})
// 이동 중인 애니메이션을 멈춘 뒤 해제 (Leaflet _leaflet_pos 오류 방지)
onBeforeUnmount(() => { resize?.disconnect(); map?.stop(); map?.off(); map?.remove(); map = null })
</script>

<style scoped>
.pm { position: relative; height: 100%; min-height: 420px; border-radius: 14px; overflow: hidden; background: #eef1f6; }
.canvas { position: absolute; inset: 0; }
.canvas :deep(.leaflet-tile-pane) { filter: saturate(.7) brightness(1.03); }
.layer-tog { position: absolute; left: 14px; top: 14px; z-index: 500; display: flex; padding: 3px; border-radius: 999px; background: #fff; box-shadow: 0 2px 10px rgba(0, 0, 0, .12); }
.layer-tog button { padding: 5px 16px; border-radius: 999px; background: none; color: var(--muted); font-size: 13px; }
.layer-tog button.on { background: var(--accent-deep); color: #fff; }
.zoom { position: absolute; right: 14px; top: 14px; z-index: 500; display: grid; gap: 8px; }
.zoom button { display: grid; place-items: center; width: 38px; height: 38px; padding: 0; border-radius: 12px; background: #fff; color: var(--ink); box-shadow: 0 2px 10px rgba(0, 0, 0, .12); }
.locate { position: absolute; left: 14px; bottom: 14px; z-index: 500; display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 999px; background: #fff; color: var(--ink); font-size: 13px; box-shadow: 0 2px 10px rgba(0, 0, 0, .12); }
.loc-err { position: absolute; left: 14px; bottom: 56px; z-index: 500; margin: 0; padding: 6px 10px; border-radius: 8px; background: #fff; color: var(--i-red); font-size: 12.5px; }
.legend { position: absolute; right: 14px; bottom: 22px; z-index: 500; margin: 0; padding: 10px 14px; list-style: none; border-radius: 12px; background: rgba(255, 255, 255, .95); box-shadow: 0 2px 10px rgba(0, 0, 0, .1); font-size: 12.5px; display: grid; gap: 5px; }
.legend i { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border-radius: 4px; vertical-align: -1px; }
.pop { position: absolute; left: 50%; top: 46%; z-index: 600; transform: translate(-50%, -100%); display: flex; align-items: center; gap: 12px; min-width: 240px; padding: 8px 14px 8px 8px; border-radius: 12px; background: #fff; box-shadow: 0 8px 24px rgba(20, 40, 90, .2); text-decoration: none; }
.pop .th { width: 56px; height: 44px; border-radius: 8px; overflow: hidden; flex: none; }
.pop .th img, .pop .th :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.pop b { display: block; font-size: 14px; }
.pop small { font-size: 12px; color: var(--muted); }
.pop .go { margin-left: auto; color: var(--faint); }
:deep(.pm-pin) { background: none; border: 0; }
</style>
