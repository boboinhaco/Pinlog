<template>
  <!-- 프로필 사진이 없을 때 쓰는 선셋 톤 해안 마을 일러스트 -->
  <svg viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient :id="`${u}sky`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd6c4" /><stop offset="1" stop-color="#fff5ee" /></linearGradient>
      <linearGradient :id="`${u}sea`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8e6fe0" /><stop offset="1" stop-color="#5245c7" /></linearGradient>
      <filter :id="`${u}blur`"><feGaussianBlur stdDeviation="2.2" /></filter>
    </defs>
    <rect width="200" height="200" :fill="`url(#${u}sky)`" />
    <path d="M0 78 L40 52 L70 66 L110 40 L150 62 L200 48 L200 96 L0 96 Z" fill="#c9a3c9" opacity=".7" :filter="`url(#${u}blur)`" />
    <rect y="92" width="200" height="108" :fill="`url(#${u}sea)`" />
    <g fill="#fff" opacity=".35"><rect x="20" y="120" width="40" height="1.5" /><rect x="90" y="140" width="60" height="1.5" /><rect x="40" y="170" width="50" height="1.5" /></g>
    <path d="M0 130 L60 112 L120 124 L200 108 L200 200 L0 200 Z" fill="#e9dccb" opacity=".25" />
    <g v-for="(h, i) in HOUSES" :key="i">
      <rect :x="h[0]" :y="h[1]" :width="h[2]" :height="h[3]" fill="#fff" />
      <rect :x="h[0] + h[2] * .35" :y="h[1] + h[3] * .45" :width="h[2] * .28" :height="h[3] * .35" fill="#8e6fe0" />
    </g>
    <path d="M128 96 a10 10 0 0 1 20 0 z" fill="#7a4fd6" /><rect x="128" y="96" width="20" height="16" fill="#fff" />
  </svg>
</template>

<script setup>
const u = `sc${Math.random().toString(36).slice(2, 8)}`  // 인스턴스별 gradient id
const HOUSES = [[8, 104, 26, 20], [36, 98, 22, 26], [60, 108, 30, 18], [94, 100, 26, 24], [150, 104, 28, 22], [178, 98, 22, 28], [20, 126, 30, 18], [110, 118, 24, 20]]
</script>
