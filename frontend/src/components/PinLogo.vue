<template>
  <span class="logo">
    <span class="mark" :style="{ width: size + 'px', height: size + 'px' }">
      <MapPin :size="size * .62" :stroke-width="2.4" color="#fff" />
    </span>
    <b :style="{ fontSize: size * .82 + 'px' }">{{ BRAND }}</b>
  </span>
</template>

<script setup>
import { MapPin } from 'lucide-vue-next'
import { BRAND } from '../utils/brand'
defineProps({ size: { type: Number, default: 32 } })
</script>

<style scoped>
.logo { display: inline-flex; align-items: center; gap: 9px; }
.mark { display: grid; place-items: center; border-radius: 30%; background: var(--grad); box-shadow: 0 4px 12px rgba(214, 41, 118, .25); }
b { font-weight: 800; letter-spacing: -.045em; color: var(--ink); line-height: 1; }
</style>
