<template>
  <header class="cover-wrap">
    <div class="cover" :style="{ height }">
      <img v-if="cover" :src="cover" alt="" />
      <slot v-else name="art"><CoverArt /></slot>
      <div class="shade"></div>
      <div class="title-box">
        <slot name="eyebrow" />
        <h1>{{ title }}</h1>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>
      <label v-if="editable" class="change">
        커버 변경
        <input type="file" accept="image/jpeg,image/png,image/webp" hidden @change="onCover" />
      </label>
      <button v-if="editable && cover" class="change reset" @click="emit('change', null)">기본 커버</button>
    </div>
    <div class="icon"><slot name="icon"><SproutIcon :size="72" /></slot></div>
    <p v-if="error" class="err">{{ error }}</p>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { fileToDataUrl } from '../utils/image'
import CoverArt from './CoverArt.vue'
import SproutIcon from './SproutIcon.vue'

// 제목이 올라간 배경 커버 (editable이면 사용자 사진으로 교체)
defineProps({ title: String, subtitle: String, cover: String, editable: Boolean, height: { type: String, default: '260px' } })
const emit = defineEmits(['change'])
const error = ref('')
async function onCover(e) {
  const file = e.target.files?.[0]; e.target.value = ''
  if (!file) return
  error.value = ''
  try { emit('change', await fileToDataUrl(file, 1800)) } catch (err) { error.value = err.message }
}
</script>

<style scoped>
.cover-wrap { position: relative; margin-bottom: 44px; }
.cover { position: relative; overflow: hidden; background: #cfdcc6; }
.cover img, .cover :deep(svg) { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0, 0, 0, 0) 30%, rgba(20, 30, 18, .42) 100%); }
.title-box { position: absolute; left: 0; right: 0; bottom: 0; max-width: 1040px; margin: 0 auto; padding: 0 48px 26px 150px; color: #fff; }
.title-box h1 { margin: 0; font-size: clamp(28px, 4.2vw, 44px); line-height: 1.2; text-shadow: 0 2px 16px rgba(0, 0, 0, .25); }
.title-box p { margin: 6px 0 0; font-size: 15px; opacity: .95; text-shadow: 0 1px 8px rgba(0, 0, 0, .3); }
.change { position: absolute; top: 12px; right: 16px; padding: 4px 10px; border-radius: 4px; background: rgba(255, 255, 255, .85); color: var(--muted); font-size: 12.5px; font-weight: 500; cursor: pointer; opacity: 0; transition: opacity .15s; }
.change.reset { right: 100px; }
.cover:hover .change, .change:focus-within { opacity: 1; }
.icon { position: absolute; left: max(48px, calc((100% - 1040px) / 2 + 48px)); bottom: -36px; width: 84px; height: 84px; display: grid; place-items: center; border-radius: 12px; background: #fff; box-shadow: 0 2px 10px rgba(15, 15, 15, .1); }
.err { max-width: 1040px; margin: 8px auto 0; padding: 0 48px; color: var(--i-red); font-size: 13px; }
@media (hover: none) { .change { opacity: 1; } }
@media (max-width: 760px) {
  .title-box { padding: 0 16px 20px 16px; }
  .icon { left: 16px; width: 64px; height: 64px; bottom: -30px; }
  .icon :deep(svg) { width: 52px; height: 52px; }
  .title-box { padding-bottom: 44px; }
}
</style>
