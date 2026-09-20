<template>
  <div class="map-wrap" :style="{ height }">
    <div ref="el" class="map-canvas"></div>
    <RouterLink v-if="expandTo" :to="expandTo" class="expand" aria-label="지도 크게 보기">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 4h6v6M20 4l-7 7M10 20H4v-6M4 20l7-7" /></svg>
    </RouterLink>
    <p v-if="!pins.length" class="map-empty">저장된 장소가 여기에 표시돼요</p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// places: [{name, lat, lng}], 좌표 없는 장소는 제외
const props = defineProps({ places: { type: Array, default: () => [] }, height: { type: String, default: '210px' }, expandTo: String })
const el = ref(null)
const pins = computed(() => props.places.filter(p => p.lat != null && p.lng != null))
let map, layer, resize

const pinIcon = name => L.divIcon({
  className: 'nx-pin', iconSize: null, iconAnchor: [11, 28],
  html: `<svg width="22" height="28" viewBox="0 0 22 28"><path d="M11 0C4.9 0 0 4.8 0 10.8 0 18.9 11 28 11 28s11-9.1 11-17.2C22 4.8 17.1 0 11 0z" fill="#4a72d8"/><circle cx="11" cy="10.5" r="4" fill="#fff"/></svg><span>${name.replace(/</g, '&lt;')}</span>`
})

function render() {
  layer.clearLayers()
  pins.value.forEach(p => L.marker([p.lat, p.lng], { icon: pinIcon(p.name) }).addTo(layer))
  if (pins.value.length > 1) map.fitBounds(L.latLngBounds(pins.value.map(p => [p.lat, p.lng])), { padding: [36, 36], animate: false })
  else if (pins.value.length === 1) map.setView([pins.value[0].lat, pins.value[0].lng], 13, { animate: false })
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: false, attributionControl: true, scrollWheelZoom: false }).setView([37.535, 127.03], 11)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap' }).addTo(map)
  layer = L.layerGroup().addTo(map)
  render()
  // 레이아웃이 늦게 잡히는 경우(데이터 로드 후 표시 등) 크기 재계산
  resize = new ResizeObserver(() => map?.invalidateSize({ animate: false }))
  resize.observe(el.value)
})
watch(pins, () => map && render())
// 이동 중인 애니메이션을 멈춘 뒤 해제 (Leaflet _leaflet_pos 오류 방지)
onBeforeUnmount(() => { resize?.disconnect(); map?.stop(); map?.off(); map?.remove(); map = null })
</script>

<style scoped>
.map-wrap { position: relative; border-radius: 8px; overflow: hidden; background: #eef1f3; }
.map-canvas { position: absolute; inset: 0; }
.expand { position: absolute; top: 10px; right: 10px; z-index: 500; width: 32px; height: 32px; border-radius: 50%; background: #fff; display: grid; place-items: center; color: var(--ink); box-shadow: 0 2px 8px rgba(0,0,0,.12); }
.map-empty { position: absolute; inset: auto 0 12px; z-index: 500; margin: 0; text-align: center; font-size: 13px; color: var(--muted); }
:deep(.nx-pin) { display: flex; align-items: flex-end; gap: 4px; white-space: nowrap; }
:deep(.nx-pin span) { margin-bottom: 8px; padding: 2px 7px; border-radius: 4px; background: #fff; font-family: var(--serif); font-size: 12px; font-weight: 600; color: var(--ink); box-shadow: 0 1px 4px rgba(0,0,0,.15); }
:deep(.leaflet-control-attribution) { font-size: 9px; }
:deep(.leaflet-tile-pane) { filter: saturate(.55) brightness(1.04) sepia(.08); }
</style>
