<template>
  <div class="login-page">
    <RouterLink to="/" class="brand"><SproutIcon :size="22" />NEXTO</RouterLink>
    <div class="box">
      <div class="arch"><ArchArt /></div>
      <h1>{{ mode === 'signup' ? 'NEXTO 시작하기' : 'NEXTO에 로그인' }}</h1>
      <p v-if="route.query.expired" class="note">세션이 끝났어요. 다시 로그인해 주세요.</p>
      <p v-else class="note">내가 확인한 일정과 장소를 계정에 모아둘 수 있어요.</p>
      <AuthForm :initial-mode="route.query.mode === 'signup' ? 'signup' : 'login'" @mode="m => (mode = m)" @done="goNext" />
      <div class="or"><span>또는</span></div>
      <button class="ghost demo" :disabled="busy" @click="demo">로그인 없이 둘러보기 (데모)</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AuthForm from '../components/AuthForm.vue'
import ArchArt from '../components/ArchArt.vue'
import SproutIcon from '../components/SproutIcon.vue'

const route = useRoute(), router = useRouter(), auth = useAuthStore()
const mode = ref('login'), busy = ref(false)
// 외부 주소로 튀지 않도록 앱 내부 경로만 허용
const goNext = () => router.push(typeof route.query.next === 'string' && route.query.next.startsWith('/') && !route.query.next.startsWith('//') ? route.query.next : '/home')
async function demo() {
  busy.value = true
  try { await auth.demo(); goNext() } finally { busy.value = false }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: grid; place-items: center; padding: 72px 16px 40px; background: linear-gradient(180deg, #f3f7f1 0%, #fff 60%); }
.brand { position: absolute; top: 16px; left: 20px; display: flex; align-items: center; gap: 6px; color: var(--ink); text-decoration: none; font-family: var(--serif); font-weight: 700; }
.box { width: 100%; max-width: 360px; }
.arch { width: 120px; aspect-ratio: 5 / 6; margin: 0 auto 18px; border-radius: 999px 999px 8px 8px; overflow: hidden; }
.arch :deep(svg) { width: 100%; height: 100%; display: block; }
h1 { margin: 0 0 6px; text-align: center; font-size: 24px; }
.note { margin: 0 0 20px; text-align: center; color: var(--muted); font-size: 14px; }
.box :deep(button:not(.text)) { height: 40px; }
.or { position: relative; margin: 18px 0; text-align: center; font-size: 12px; color: var(--faint); }
.or::before { content: ''; position: absolute; left: 0; right: 0; top: 50%; border-top: 1px solid var(--line); }
.or span { position: relative; padding: 0 10px; background: #fff; }
.demo { width: 100%; }
</style>
