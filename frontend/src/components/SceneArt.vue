<template>
  <!-- 사진 대신 쓰는 선셋 톤 풍경 일러스트 -->
  <svg viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient :id="`${u}sky`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd6c4" /><stop offset="1" stop-color="#fff5ee" /></linearGradient>
      <linearGradient :id="`${u}sea`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8e6fe0" /><stop offset="1" stop-color="#5245c7" /></linearGradient>
      <filter :id="`${u}blur`"><feGaussianBlur stdDeviation="2.2" /></filter>
    </defs>

    <!-- 해안 마을 -->
    <g v-if="scene === 'coast'">
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
    </g>

    <!-- 하얀 집들 -->
    <g v-else-if="scene === 'houses'">
      <rect width="200" height="200" fill="#fde3ec" />
      <rect x="10" y="60" width="70" height="140" fill="#fff" /><rect x="70" y="30" width="60" height="170" fill="#fbf7f8" /><rect x="120" y="80" width="80" height="120" fill="#fff" />
      <path d="M78 30 a22 22 0 0 1 44 0 z" fill="#8a55e0" /><rect x="96" y="4" width="8" height="10" fill="#fff" /><path d="M100 0 v8" stroke="#fff" stroke-width="2" />
      <g fill="#8e6fe0"><rect x="28" y="92" width="14" height="22" rx="7" /><rect x="90" y="70" width="16" height="26" rx="8" /><rect x="140" y="110" width="14" height="20" rx="7" /><rect x="168" y="110" width="14" height="20" rx="7" /></g>
      <g fill="#ecd6e4"><rect x="10" y="140" width="190" height="4" /><rect x="10" y="176" width="190" height="4" /></g>
      <g fill="#8fb88a"><circle cx="40" cy="150" r="10" /><circle cx="170" cy="160" r="9" /></g>
      <g fill="#f3a9c0"><circle cx="36" cy="146" r="2.4" /><circle cx="46" cy="152" r="2.4" /><circle cx="166" cy="156" r="2.4" /></g>
    </g>

    <!-- 창밖 바다 -->
    <g v-else-if="scene === 'window'">
      <rect width="200" height="200" fill="#fbf0f4" />
      <rect x="30" y="20" width="140" height="170" :fill="`url(#${u}sky)`" />
      <rect x="30" y="118" width="140" height="72" :fill="`url(#${u}sea)`" />
      <path d="M30 118 Q70 106 100 116 T170 110 V118 H30 Z" fill="#e3c3dc" />
      <g stroke="#fff" stroke-width="7" fill="none"><rect x="30" y="20" width="140" height="170" /><path d="M100 20 V190 M30 100 H170" /></g>
      <path d="M170 20 C150 60 160 120 150 190 L200 190 L200 20 Z" fill="#fff" opacity=".85" />
      <g fill="#7ea46e"><ellipse cx="46" cy="186" rx="18" ry="8" /><ellipse cx="60" cy="178" rx="8" ry="14" transform="rotate(20 60 178)" /></g>
    </g>

    <!-- 흰 들꽃 -->
    <g v-else-if="scene === 'flowers'">
      <rect width="200" height="200" fill="#fde6ef" />
      <g :filter="`url(#${u}blur)`" opacity=".6"><circle cx="30" cy="40" r="26" fill="#f7c6da" /><circle cx="170" cy="170" r="30" fill="#e9d3f5" /></g>
      <g stroke="#7fa274" stroke-width="2"><path d="M60 200 L70 120" /><path d="M110 200 L100 90" /><path d="M150 200 L140 130" /><path d="M30 200 L44 150" /></g>
      <g v-for="(f, i) in FLOWERS" :key="i" :transform="`translate(${f[0]} ${f[1]}) scale(${f[2]})`">
        <ellipse v-for="r in [0, 45, 90, 135, 180, 225, 270, 315]" :key="r" cx="0" cy="-10" rx="4.2" ry="10" fill="#fff" :transform="`rotate(${r})`" />
        <circle r="4.5" fill="#f2c94c" />
      </g>
    </g>

    <!-- 커피 -->
    <g v-else-if="scene === 'coffee'">
      <rect width="200" height="200" fill="#fbf5f2" />
      <path d="M0 0 H200 V40 C140 60 60 30 0 50 Z" fill="#f6e6ee" />
      <circle cx="104" cy="112" r="56" fill="#fff" /><circle cx="104" cy="112" r="56" fill="none" stroke="#e1e6ef" stroke-width="2" />
      <circle cx="104" cy="112" r="36" fill="#f8f9fb" stroke="#e5e9f0" stroke-width="3" />
      <circle cx="104" cy="112" r="26" fill="#3b2a22" /><circle cx="98" cy="106" r="7" fill="#6b4c3d" opacity=".6" />
      <path d="M142 118 q18 0 18 -10" stroke="#e5e9f0" stroke-width="7" fill="none" stroke-linecap="round" />
      <rect x="20" y="170" width="60" height="5" rx="2.5" fill="#c8cfdb" transform="rotate(-10 50 172)" />
    </g>

    <!-- 테라스: 흰 벽 아치 너머 바다 -->
    <g v-else-if="scene === 'terrace'">
      <rect width="200" height="200" :fill="`url(#${u}sky)`" />
      <path d="M0 104 L50 92 L100 100 L150 88 L200 98 L200 110 L0 110 Z" fill="#d6a9c8" opacity=".7" />
      <rect y="108" width="200" height="92" :fill="`url(#${u}sea)`" />
      <g fill="#fff" opacity=".35"><rect x="110" y="128" width="50" height="1.5" /><rect x="130" y="150" width="40" height="1.5" /></g>
      <path d="M0 0 H70 V200 H0 Z M16 60 a19 19 0 0 1 38 0 V124 H16 Z" fill="#fbfcfe" fill-rule="evenodd" />
      <rect x="0" y="150" width="200" height="50" fill="#fbf6f7" />
      <g fill="#fff" stroke="#efe3ea" stroke-width="1.5"><rect x="70" y="138" width="130" height="12" /><rect x="84" y="150" width="8" height="30" /><rect x="120" y="150" width="8" height="30" /><rect x="156" y="150" width="8" height="30" /><rect x="190" y="150" width="8" height="30" /></g>
      <path d="M150 138 C146 120 140 110 132 104 M150 138 C154 118 164 108 172 104 M150 138 C150 122 152 112 156 100" stroke="#6f955f" stroke-width="2.4" fill="none" />
      <g fill="#8fb77c"><ellipse cx="132" cy="104" rx="9" ry="5" transform="rotate(-30 132 104)" /><ellipse cx="172" cy="104" rx="9" ry="5" transform="rotate(30 172 104)" /><ellipse cx="156" cy="98" rx="5" ry="9" /></g>
      <path d="M140 138 h20 l-3 14 h-14 z" fill="#d9c3ad" />
    </g>

    <!-- 바다와 집 (기본) -->
    <g v-else>
      <rect width="200" height="200" :fill="`url(#${u}sky)`" />
      <rect y="100" width="200" height="100" :fill="`url(#${u}sea)`" />
      <rect x="40" y="120" width="70" height="80" fill="#fff" /><rect x="96" y="140" width="60" height="60" fill="#fbf7f8" />
      <g fill="#8a55e0"><rect x="54" y="140" width="12" height="18" /><rect x="82" y="140" width="12" height="18" /><rect x="116" y="156" width="12" height="16" /></g>
      <g fill="#7fa274"><circle cx="30" cy="190" r="16" /><circle cx="170" cy="186" r="14" /></g>
    </g>
  </svg>
</template>

<script setup>
// scene: coast | houses | window | flowers | coffee | terrace | sea
defineProps({ scene: { type: String, default: 'sea' } })
const u = `sc${Math.random().toString(36).slice(2, 8)}`  // 인스턴스별 gradient id
const HOUSES = [[8, 104, 26, 20], [36, 98, 22, 26], [60, 108, 30, 18], [94, 100, 26, 24], [150, 104, 28, 22], [178, 98, 22, 28], [20, 126, 30, 18], [110, 118, 24, 20]]
const FLOWERS = [[70, 116, 1.1], [100, 86, 1.3], [140, 126, 1], [44, 148, .9], [128, 70, .8], [170, 96, .9], [84, 150, .8]]
</script>
