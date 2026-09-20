<template>
  <Teleport to="body">
    <div class="backdrop" @click.self="emit('close')">
      <div class="sheet" role="dialog" aria-modal="true" :aria-label="title">
        <div class="hd"><b>{{ title }}</b><button class="text" aria-label="닫기" @click="emit('close')">✕</button></div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
// 간단한 모달 (ESC·바깥 클릭으로 닫기)
defineProps({ title: String })
const emit = defineEmits(['close'])
const onKey = e => e.key === 'Escape' && emit('close')
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<style scoped>
.backdrop { position: fixed; inset: 0; z-index: 3000; display: grid; place-items: center; padding: 16px; background: rgba(20, 30, 60, .35); }
.sheet { width: 100%; max-width: 440px; padding: 18px 20px 20px; background: #fff; border-radius: 16px; box-shadow: 0 20px 50px rgba(20, 40, 90, .25); }
.hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 17px; }
</style>
