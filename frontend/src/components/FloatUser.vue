<template>
  <div ref="root" class="fu" :class="{ hero }">
    <UserMenu :open="open" @toggle="open = !open" @close="open = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import UserMenu from './UserMenu.vue'

// 데스크톱(사이드바 레이아웃)용 오른쪽 위 사용자 메뉴; hero면 콜라주 위에 겹침
defineProps({ hero: Boolean })
const root = ref(null), open = ref(false)
const onDoc = e => { if (root.value && !root.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('click', onDoc))
onBeforeUnmount(() => document.removeEventListener('click', onDoc))
</script>

<style scoped>
.fu { position: absolute; top: 12px; right: 20px; z-index: 900; }
.fu.hero :deep(.who) { background: rgba(255, 255, 255, .92); backdrop-filter: blur(8px); box-shadow: 0 2px 10px rgba(0, 0, 0, .1); }
</style>
