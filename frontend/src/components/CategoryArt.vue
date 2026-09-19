<template>
  <!-- 카테고리 블록 일러스트 (파스텔 소품 + 별·클로버 장식) -->
  <svg viewBox="0 0 200 120" :preserveAspectRatio="fill ? 'xMidYMid slice' : 'xMidYMid meet'" aria-hidden="true">
    <rect width="200" height="120" :fill="BG[kind]" />
    <!-- 공통 장식 -->
    <g opacity=".9">
      <path :d="star(28, 26, 9)" :fill="ACC[kind][0]" />
      <path :d="star(172, 96, 7)" :fill="ACC[kind][1]" />
      <g :transform="`translate(166 22) scale(.8)`" :fill="ACC[kind][2]">
        <circle cx="-5" cy="0" r="5" /><circle cx="5" cy="0" r="5" /><circle cx="0" cy="-5" r="5" /><circle cx="0" cy="5" r="5" />
      </g>
      <circle cx="40" cy="98" r="3" :fill="ACC[kind][1]" /><circle cx="150" cy="48" r="2.5" :fill="ACC[kind][0]" />
    </g>

    <g v-if="kind === 'POLICY_HOUSING'">
      <rect x="72" y="56" width="56" height="44" rx="4" fill="#fff" stroke="#8fb58a" stroke-width="3" />
      <path d="M64 60 L100 30 L136 60 Z" fill="#a8d1a1" stroke="#7aa874" stroke-width="3" stroke-linejoin="round" />
      <rect x="92" y="76" width="16" height="24" rx="3" fill="#f6c9a6" />
      <rect x="78" y="64" width="11" height="10" rx="2" fill="#dcefd8" /><rect x="111" y="64" width="11" height="10" rx="2" fill="#dcefd8" />
      <path d="M100 50 c-4 -5 -10 -1 -6 4 l6 5 l6 -5 c4 -5 -2 -9 -6 -4z" fill="#f29bb0" />
    </g>
    <g v-else-if="kind === 'FINANCE'">
      <ellipse cx="96" cy="72" rx="34" ry="26" fill="#f8c1cf" />
      <circle cx="126" cy="66" r="10" fill="#f8c1cf" /><ellipse cx="129" cy="68" rx="4" ry="3" fill="#e99aae" />
      <path d="M80 50 l6 -10 l6 10z" fill="#f4a7ba" /><circle cx="112" cy="62" r="2.4" fill="#5a4a50" />
      <rect x="84" y="94" width="8" height="10" rx="3" fill="#f4a7ba" /><rect x="104" y="94" width="8" height="10" rx="3" fill="#f4a7ba" />
      <rect x="88" y="47" width="18" height="4" rx="2" fill="#d97f96" />
      <g fill="#f3cf6b" stroke="#d9ab35" stroke-width="2"><circle cx="58" cy="86" r="10" /><circle cx="64" cy="70" r="8" /></g>
      <text x="58" y="90" font-size="10" text-anchor="middle" fill="#b8871f" font-weight="700">₩</text>
    </g>
    <g v-else-if="kind === 'EVENT'">
      <path d="M50 44 Q100 64 150 44" stroke="#c9a8e0" stroke-width="2" fill="none" />
      <g><path d="M60 48 l6 12 l6 -9z" fill="#f7a8bf" /><path d="M84 54 l5 12 l7 -10z" fill="#f9d37a" /><path d="M108 55 l6 11 l6 -11z" fill="#a8d6c0" /><path d="M132 50 l6 11 l6 -12z" fill="#b8c9f2" /></g>
      <path d="M68 104 L68 76 L100 62 L132 76 L132 104 Z" fill="#fff" stroke="#f29bb0" stroke-width="3" stroke-linejoin="round" />
      <path d="M100 62 L100 104" stroke="#f29bb0" stroke-width="3" /><path d="M84 104 Q100 84 116 104" fill="#fde3ea" />
      <g fill="#8a6fb3"><circle cx="146" cy="84" r="4" /><rect x="149" y="66" width="2.4" height="18" /><path d="M151 66 q8 3 6 10 q-1 -5 -6 -5z" /></g>
    </g>
    <g v-else-if="kind === 'POLICY_JOB'">
      <rect x="66" y="50" width="68" height="48" rx="8" fill="#9cc1e6" stroke="#6f9cc9" stroke-width="3" />
      <path d="M88 50 v-8 a6 6 0 0 1 6 -6 h12 a6 6 0 0 1 6 6 v8" fill="none" stroke="#6f9cc9" stroke-width="3" />
      <rect x="66" y="68" width="68" height="6" fill="#6f9cc9" /><rect x="94" y="64" width="12" height="14" rx="3" fill="#f9d37a" />
      <path :d="star(140, 44, 10)" fill="#f9d37a" />
    </g>
    <g v-else-if="kind === 'POLICY_LIVING'">
      <path d="M68 58 h64 l-7 42 h-50 z" fill="#f8c89e" stroke="#e39a5d" stroke-width="3" stroke-linejoin="round" />
      <path d="M82 58 q18 -30 36 0" fill="none" stroke="#e39a5d" stroke-width="3" />
      <circle cx="88" cy="54" r="10" fill="#f28b8b" /><path d="M88 44 q4 -6 9 -4" stroke="#6a8f4e" stroke-width="2.4" fill="none" />
      <ellipse cx="112" cy="50" rx="7" ry="12" fill="#a8d1a1" transform="rotate(25 112 50)" />
      <path d="M100 86 c-5 -7 -14 -1 -8 6 l8 7 l8 -7 c6 -7 -3 -13 -8 -6z" fill="#fff" />
    </g>
    <g v-else-if="kind === 'SUBSCRIPTION'">
      <rect x="62" y="36" width="36" height="66" rx="3" fill="#e8d4c4" stroke="#b58f73" stroke-width="3" />
      <rect x="98" y="54" width="40" height="48" rx="3" fill="#f3e6da" stroke="#b58f73" stroke-width="3" />
      <g fill="#fff"><rect x="69" y="44" width="8" height="8" /><rect x="83" y="44" width="8" height="8" /><rect x="69" y="60" width="8" height="8" /><rect x="83" y="60" width="8" height="8" /><rect x="69" y="76" width="8" height="8" /><rect x="83" y="76" width="8" height="8" /><rect x="106" y="62" width="9" height="8" /><rect x="121" y="62" width="9" height="8" /><rect x="106" y="78" width="9" height="8" /><rect x="121" y="78" width="9" height="8" /></g>
      <g transform="translate(142 34) rotate(35)"><circle r="9" fill="none" stroke="#e0b44a" stroke-width="4" /><rect x="7" y="-2.5" width="22" height="5" rx="2" fill="#e0b44a" /><rect x="22" y="2" width="4" height="6" fill="#e0b44a" /></g>
    </g>
    <g v-else-if="kind === 'RECRUIT'">
      <path d="M70 66 l44 -22 v56 l-44 -22 z" fill="#cdb8ee" stroke="#9b7fcf" stroke-width="3" stroke-linejoin="round" />
      <rect x="58" y="64" width="14" height="18" rx="4" fill="#9b7fcf" />
      <path d="M76 82 l6 18 h10 l-6 -16" fill="#b69ce2" />
      <g stroke="#f29bb0" stroke-width="3" stroke-linecap="round"><path d="M124 56 l12 -8" /><path d="M126 72 h14" /><path d="M124 88 l12 8" /></g>
    </g>
    <g v-else-if="kind === 'CONTEST'">
      <path d="M78 38 h44 v18 a22 22 0 0 1 -44 0 z" fill="#f6cf6a" stroke="#d5a532" stroke-width="3" />
      <path d="M78 44 h-10 a10 10 0 0 0 12 14" fill="none" stroke="#d5a532" stroke-width="3" /><path d="M122 44 h10 a10 10 0 0 1 -12 14" fill="none" stroke="#d5a532" stroke-width="3" />
      <rect x="95" y="76" width="10" height="12" fill="#d5a532" /><rect x="82" y="88" width="36" height="12" rx="3" fill="#f28b8b" />
      <path :d="star(100, 52, 8)" fill="#fff" />
    </g>
    <g v-else>
      <path :d="star(100, 60, 26)" fill="#f9d37a" stroke="#e0b44a" stroke-width="3" stroke-linejoin="round" />
      <circle cx="92" cy="58" r="2.6" fill="#5a4a50" /><circle cx="108" cy="58" r="2.6" fill="#5a4a50" />
      <path d="M94 66 q6 5 12 0" stroke="#5a4a50" stroke-width="2" fill="none" stroke-linecap="round" />
      <path :d="star(62, 80, 8)" fill="#f7a8bf" /><path :d="star(140, 36, 7)" fill="#a8d6c0" />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ kind: { type: String, default: 'OTHER' }, fill: Boolean })
const BG = {
  POLICY_HOUSING: '#f3f8f1', FINANCE: '#fdf6ea', EVENT: '#fdf2f5', POLICY_JOB: '#f0f5fb', POLICY_LIVING: '#fdf3ea',
  SUBSCRIPTION: '#f8f3ef', RECRUIT: '#f6f2fb', CONTEST: '#fdf1f0', OTHER: '#f6f6f3'
}
const ACC = {
  POLICY_HOUSING: ['#f9d37a', '#f7a8bf', '#a8d1a1'], FINANCE: ['#f7a8bf', '#a8d1a1', '#f3cf6b'], EVENT: ['#b8c9f2', '#f9d37a', '#a8d6c0'],
  POLICY_JOB: ['#f7a8bf', '#a8d1a1', '#b8c9f2'], POLICY_LIVING: ['#a8d1a1', '#f7a8bf', '#f9d37a'], SUBSCRIPTION: ['#a8d1a1', '#f7a8bf', '#d8c2ad'],
  RECRUIT: ['#f9d37a', '#a8d6c0', '#cdb8ee'], CONTEST: ['#b8c9f2', '#a8d1a1', '#f28b8b'], OTHER: ['#cdb8ee', '#f7a8bf', '#a8d1a1']
}
const kind = computed(() => props.kind in BG ? props.kind : 'OTHER')

// 5각 별 path
function star(cx, cy, r) {
  const pts = Array.from({ length: 10 }, (_, i) => {
    const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r
    return `${(cx + rr * Math.cos(a)).toFixed(1)} ${(cy + rr * Math.sin(a)).toFixed(1)}`
  })
  return `M${pts.join(' L')} Z`
}
</script>
