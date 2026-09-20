<template>
  <RouterLink :to="`/items/${item.id}`" class="ecard" :class="{ ended }">
    <div class="img">
      <img v-if="item.image && imgOk" :src="item.image" alt="" referrerpolicy="no-referrer" @error="imgOk = false" />
      <CategoryArt v-else :kind="item.category" fill />
      <span class="cat tag" :class="`tone-${CATEGORY[item.category]?.tone ?? 'gray'}`">{{ CATEGORY[item.category]?.label ?? '기타' }}</span>
      <button class="heart" :class="{ on: liked, pop }" :aria-pressed="liked" :aria-label="liked ? '좋아요 취소' : '좋아요'" @click.prevent.stop="toggle">
        <Heart :size="17" :stroke-width="2.2" :fill="liked ? 'currentColor' : 'none'" />
      </button>
      <span v-if="ended" class="over"><CircleCheck :size="14" />종료됨</span>
    </div>
    <div class="body">
      <b><span v-if="ended" class="endtag">종료됨</span>{{ item.title }}</b>
      <span v-if="!item.start && item.products?.length" class="meta"><ShoppingBag :size="14" />상품 {{ item.products.length }}개 · 링크 확인</span>
      <span v-else class="meta"><CalendarDays :size="14" />{{ periodLong(item.start, item.end) }}</span>
      <span v-if="item.place?.name" class="meta"><MapPin :size="14" />{{ item.place.address || item.place.name }}</span>
    </div>
  </RouterLink>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Heart, CalendarDays, MapPin, ShoppingBag, CircleCheck } from 'lucide-vue-next'
import { patchItem } from '../api/nexto'
import { CATEGORY } from '../utils/labels'
import { periodLong, isEnded } from '../utils/events'
import CategoryArt from './CategoryArt.vue'

// 일정 카드 + 좋아요(항목 fields.liked에 저장). 마감·종료가 지난 항목은 흐리게 + '종료됨'
const props = defineProps({ item: { type: Object, required: true } })
const emit = defineEmits(['liked'])
const imgOk = ref(true), liked = ref(props.item.liked), pop = ref(false)
const ended = computed(() => isEnded(props.item))
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
.img > img, .img > :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .4s; }
.ecard:hover .img img { transform: scale(1.04); }
.cat { position: absolute; left: 10px; top: 10px; padding: 3px 11px; backdrop-filter: blur(6px); box-shadow: 0 1px 4px rgba(0, 0, 0, .08); }
.heart { position: absolute; right: 10px; top: 10px; width: 28px; height: 28px; padding: 0; border-radius: 50%; background: rgba(255, 255, 255, .92); color: var(--ink); display: grid; place-items: center; box-shadow: 0 2px 8px rgba(0, 0, 0, .12); }
.heart.on { color: #ff3040; }
.ecard.ended { opacity: .62; }
.ecard.ended:hover { opacity: .9; }
.ecard.ended .img img, .ecard.ended .img :deep(svg) { filter: grayscale(.7); }
.over { position: absolute; left: 10px; bottom: 10px; display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; background: rgba(38, 38, 38, .78); color: #fff; font-size: 12px; font-weight: 700; }
.endtag { display: inline-block; margin-right: 6px; padding: 1px 7px; border-radius: 6px; background: var(--t-gray); color: #525252; font-size: 11.5px; font-weight: 700; vertical-align: 2px; }
.heart.pop { animation: pop .35s ease; }
@keyframes pop { 40% { transform: scale(1.25); } }
.body { display: grid; gap: 5px; padding: 12px 14px 14px; }
.body b { font-size: 15px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
