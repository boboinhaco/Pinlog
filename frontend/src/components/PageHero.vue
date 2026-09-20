<template>
  <section class="ph" :class="{ left: align === 'left' }">
    <RouterLink v-if="back" :to="back" class="back"><ArrowLeft :size="16" />이전으로</RouterLink>
    <p v-if="tagline" class="hand tl">{{ tagline }}</p>
    <h1>{{ title }}</h1>
    <p v-if="sub" class="sub">{{ sub }}</p>
    <div v-if="$slots.action" class="action"><slot name="action" /></div>
    <div v-if="doodle" class="doodle" aria-hidden="true">
      <p class="hand" v-html="doodle"></p>
      <svg width="58" height="50" viewBox="0 0 70 60" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M40 20 L66 8 L52 34 L46 24 Z" /><path d="M46 24 L66 8" /><path d="M40 22 C 26 34 20 44 4 50" stroke-dasharray="3 4" /></svg>
    </div>
    <slot />
  </section>
</template>

<script setup>
import { ArrowLeft } from 'lucide-vue-next'
// 페이지 상단: 손글씨 태그라인 + 제목 + 설명 (+ 오른쪽 버튼/손글씨 낙서)
// doodle은 고정 문구만 넘길 것 (v-html)
defineProps({ title: String, tagline: String, sub: String, doodle: String, back: String, align: { type: String, default: 'center' } })
</script>

<style scoped>
.ph { position: relative; text-align: center; padding: 4px 0 6px; }
.ph.left { text-align: left; }
.back { display: inline-flex; align-items: center; gap: 6px; margin-bottom: 6px; padding: 4px 10px 4px 6px; border-radius: 10px; color: var(--muted); font-size: 14px; font-weight: 600; text-decoration: none; }
.back:hover { color: var(--ink); background: var(--hover); }
.tl { margin: 0; font-size: 22px; color: var(--hand-ink); }
h1 { margin: 2px 0 6px; font-size: clamp(28px, 3.2vw, 38px); font-weight: 800; letter-spacing: -.04em; color: var(--ink); }
.sub { margin: 0; font-size: 16px; color: var(--muted); }
.action { position: absolute; right: 0; top: 50%; transform: translateY(-50%); }
.doodle { position: absolute; right: 0; top: 4px; color: var(--hand-ink); display: flex; align-items: flex-end; gap: 2px; transform: rotate(-6deg); pointer-events: none; }
.doodle p { margin: 0; font-size: 20px; line-height: 1.2; text-align: left; }
@media (max-width: 1300px) { .doodle { display: none; } }
@media (max-width: 900px) { .action { position: static; transform: none; margin-top: 12px; } }
</style>
