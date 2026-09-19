<template>
  <aside class="arch-col">
    <!-- 아치 사진: 로그인 사용자는 눌러서 교체 -->
    <label class="arch" :class="{ editable: canEdit }" :title="canEdit ? '사진 바꾸기' : ''">
      <img v-if="auth.user?.photo" :src="auth.user.photo" alt="프로필 사진" />
      <ArchArt v-else />
      <span v-if="canEdit" class="arch-edit">사진 바꾸기</span>
      <input v-if="canEdit" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="onPhoto" />
    </label>
    <p v-if="photoError" class="err">{{ photoError }}</p>

    <div class="box">
      <!-- 로그인 상태: 인사 + 내비게이션 -->
      <template v-if="auth.user && !auth.isDemo">
        <p class="hello serif">{{ auth.displayName }}님의 페이지</p>
        <p class="mail">{{ auth.user.email }}</p>
      </template>
      <template v-else>
        <p class="hello serif">{{ mode === 'signup' ? '회원가입' : '로그인' }}</p>
        <p v-if="auth.isDemo" class="mail">지금은 데모 계정으로 보고 있어요. 로그인하면 내 저장함이 따로 생겨요.</p>
        <AuthForm class="login" @mode="m => (mode = m)" @done="router.go(0)" />
      </template>

      <h3 class="nav-title">Navigation Page</h3>
      <nav class="nav">
        <RouterLink v-for="n in NAV" :key="n.to" :to="n.to"><LeafIcon />{{ n.label }}</RouterLink>
      </nav>

      <template v-if="auth.user && !auth.isDemo">
        <h3 class="nav-title">Account</h3>
        <button class="text logout" @click="logout">로그아웃</button>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { fileToDataUrl } from '../utils/image'
import ArchArt from './ArchArt.vue'
import AuthForm from './AuthForm.vue'

const LeafIcon = () => h('svg', { width: 15, height: 15, viewBox: '0 0 24 24', 'aria-hidden': 'true' },
  [h('path', { d: 'M5 19C5 10 11 4 20 4c0 9-6 15-15 15z', fill: '#7fae6c' }), h('path', { d: 'M5 19L14 10', stroke: '#fff', 'stroke-width': 1.6 })])
const NAV = [
  { to: '/home', label: '홈' }, { to: '/calendar', label: '일정' }, { to: '/map', label: '지도' },
  { to: '/items', label: '저장됨' }, { to: '/upload', label: '스크린샷으로 올리기' }
]
const auth = useAuthStore(), router = useRouter()
const mode = ref('login'), photoError = ref('')
const canEdit = computed(() => auth.user && !auth.isDemo)

async function onPhoto(e) {
  const file = e.target.files?.[0]; e.target.value = ''
  if (!file) return
  photoError.value = ''
  try { await auth.update({ photo: await fileToDataUrl(file, 800) }) } catch (err) { photoError.value = err.message }
}

function logout() { auth.logout(); router.push('/') }
</script>

<style scoped>
.arch-col { display: grid; gap: 12px; align-content: start; }
.arch { position: relative; display: block; aspect-ratio: 5 / 6; border-radius: 999px 999px 10px 10px; overflow: hidden; background: var(--mint); }
.arch img, .arch :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.arch.editable { cursor: pointer; }
.arch-edit { position: absolute; left: 50%; bottom: 12px; transform: translateX(-50%); padding: 4px 10px; border-radius: 4px; background: rgba(255, 255, 255, .9); font-size: 12px; opacity: 0; transition: opacity .15s; white-space: nowrap; }
.arch.editable:hover .arch-edit, .arch.editable:focus-within .arch-edit { opacity: 1; }
.box { border: 1px solid var(--line); border-radius: 8px; padding: 16px; }
.hello { margin: 0 0 2px; font-size: 16px; font-weight: 700; }
.mail { margin: 0 0 12px; font-size: 13px; color: var(--muted); line-height: 1.5; }
.login { margin-bottom: 8px; }
.login :deep(input) { padding: 7px 9px; font-size: 14px; }
.err { margin: 0; color: var(--i-red); font-size: 13px; }
.nav-title { margin: 14px 0 6px; font-family: var(--serif); font-size: 14px; font-weight: 700; }
.nav { display: grid; }
.nav a { display: flex; align-items: center; gap: 8px; padding: 4px 6px; margin: 0 -6px; border-radius: 4px; font-size: 14px; text-decoration: none; }
.nav a:hover { background: var(--hover); }
.nav a.router-link-exact-active { font-weight: 600; }
.logout { padding: 4px 6px; margin: 0 -6px; font-size: 14px; }
</style>
