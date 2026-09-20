<template>
  <footer class="ftr">
    <div class="l"><PinLogo :size="26" /><span>좋아하는 것이 더 특별한 하루가 되는 곳.</span></div>
    <nav class="links">
      <RouterLink to="/">서비스 소개</RouterLink><span>이용약관</span><span>개인정보처리방침</span><span>고객센터</span>
    </nav>
    <div class="sns" aria-hidden="true"><Instagram :size="20" /><Youtube :size="20" /><MessageCircle :size="20" /></div>
    <small class="c">© {{ new Date().getFullYear() }} {{ BRAND }}. All rights reserved.</small>
  </footer>
</template>

<script setup>
import { Instagram, Youtube, MessageCircle } from 'lucide-vue-next'
import { BRAND } from '../utils/brand'
import PinLogo from './PinLogo.vue'
</script>

<style scoped>
.ftr { display: flex; flex-wrap: wrap; align-items: center; gap: 16px 32px; padding: 24px 40px; background: #fff; border-top: 1px solid var(--line); font-size: 13px; color: var(--muted); }
.l { display: flex; align-items: center; gap: 16px; flex: 1; min-width: 260px; }
.links { display: flex; gap: 22px; }
.links a { text-decoration: none; }
.links a:hover { color: var(--ink); }
.sns { display: flex; gap: 14px; color: var(--ink-2); }
.c { color: var(--faint); }
@media (max-width: 760px) { .ftr { padding: 20px 16px; } .links { flex-wrap: wrap; gap: 10px 16px; } }
</style>
