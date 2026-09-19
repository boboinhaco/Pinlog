<template>
  <!-- 페이지 아이콘: 새싹 -->
  <svg :width="size" :height="size" viewBox="0 0 64 64" aria-hidden="true">
    <path d="M32 58 C 32 46 32 38 32 30" stroke="#6a8f4e" stroke-width="4" stroke-linecap="round" fill="none" />
    <path d="M32 32 C 20 32 10 24 8 10 C 22 10 32 18 32 32 Z" fill="#9cc47e" />
    <path d="M32 28 C 42 28 54 20 56 6 C 42 6 32 14 32 28 Z" fill="#b9d98f" />
    <path d="M32 32 C 24 28 16 20 12 13" stroke="#6a8f4e" stroke-width="1.6" fill="none" opacity=".6" />
    <ellipse cx="32" cy="58" rx="14" ry="4" fill="#d9c9a8" />
  </svg>
</template>

<script setup>
defineProps({ size: { type: Number, default: 64 } })
</script>
