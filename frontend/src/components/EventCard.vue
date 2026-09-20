<template>
  <RouterLink :to="`/items/${item.id}`" class="ecard">
    <div class="img">
      <img v-if="item.image && imgOk" :src="item.image" alt="" referrerpolicy="no-referrer" @error="imgOk = false" />
      <CategoryArt v-else :kind="item.category" fill />
      <span class="cat tag" :class="`tone-${CATEGORY[item.category]?.tone ?? 'gray'}`">{{ CATEGORY[item.category]?.label ?? '기타' }}</span>
      <button class="heart" :class="{ on: liked, pop }" :aria-pressed="liked" :aria-label="liked ? '좋아요 취소' : '좋아요'" @click.prevent.stop="toggle">
        <Heart :size="15" :stroke-width="2.2" :fill="liked ? 'currentColor' : 'none'" />
      </button>
    </div>
    <div class="body">
      <b>{{ item.title }}</b>
      <span class="meta"><CalendarDays :size="14" />{{ periodLong(item.start, item.end) }}</span>
      <span v-if="item.place?.name" class="meta"><MapPin :size="14" />{{ item.place.address || item.place.name }}</span>
    </div>
  </RouterLink>
</template>

<script setup>
import { ref } from 'vue'
import { Heart, CalendarDays, MapPin } from 'lucide-vue-next'
import { patchItem } from '../api/nexto'
import { CATEGORY } from '../utils/labels'
import { periodLong } from '../utils/events'
import CategoryArt from './CategoryArt.vue'

// 일정 카드 + 좋아요(항목 fields.liked에 저장)
const props = defineProps({ item: { type: Object, required: true } })
const emit = defineEmits(['liked'])
const imgOk = ref(true), liked = ref(props.item.liked), pop = ref(false)
async function toggle() {
  liked.value = !liked.value
  if (liked.value) { pop.value = true; setTimeout(() => (pop.value = false), 350) }
  try { await patchItem(props.item.id, { fields: { liked: liked.value } }); emit('liked', liked.value) } catch { liked.value = !liked.value }
}
</script>

<style scoped>
.ecard { display: block; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; background: #fff; text-decoration: none; transition: box-shadow .2s, transform .2s; }
.ecard:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }
.img { position: relative; aspect-ratio: 4 / 3; background: var(--soft); overflow: hidden; }
.img img, .img :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .4s; }
.ecard:hover .img img { transform: scale(1.04); }
.cat { position: absolute; left: 10px; top: 10px; padding: 3px 11px; backdrop-filter: blur(6px); box-shadow: 0 1px 4px rgba(0, 0, 0, .08); }
.heart { position: absolute; right: 10px; top: 10px; width: 28px; height: 28px; padding: 0; border-radius: 50%; background: rgba(255, 255, 255, .92); color: var(--ink); display: grid; place-items: center; box-shadow: 0 2px 8px rgba(0, 0, 0, .12); }
.heart.on { color: #ff3040; }
.heart.pop { animation: pop .35s ease; }
@keyframes pop { 40% { transform: scale(1.25); } }
.body { display: grid; gap: 5px; padding: 12px 14px 14px; }
.body b { font-size: 15px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
