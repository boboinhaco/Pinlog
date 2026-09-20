<template>
  <div class="um">
    <button class="who" :aria-expanded="open" @click.stop="emit('toggle')">
      <span class="ring"><span class="avatar">
        <img v-if="auth.user?.photo" :src="auth.user.photo" alt="" />
        <SceneArt v-else />
      </span></span>
      <span class="greet">{{ auth.user && !auth.isDemo ? `${auth.displayName}님, 좋은 하루예요!` : '좋은 하루예요!' }}</span>
      <ChevronDown :size="16" class="chev" />
    </button>
    <div v-if="open" class="menu" @click.stop>
      <template v-if="auth.user && !auth.isDemo">
        <div class="me">
          <span class="ring big"><span class="avatar"><img v-if="auth.user.photo" :src="auth.user.photo" alt="" /><SceneArt v-else /></span></span>
          <span><b>{{ auth.displayName }}</b><small>{{ auth.user.email }}</small></span>
        </div>
        <label class="item"><Camera :size="18" />프로필 사진 바꾸기<input type="file" accept="image/jpeg,image/png,image/webp" hidden @change="onPhoto" /></label>
        <RouterLink to="/items" class="item" @click="emit('close')"><Bookmark :size="18" />저장한 모든 항목</RouterLink>
        <RouterLink to="/upload" class="item" @click="emit('close')"><ImagePlus :size="18" />스크린샷으로 추가</RouterLink>
        <button class="item out" @click="logout"><LogOut :size="18" />로그아웃</button>
        <p v-if="err" class="err">{{ err }}</p>
      </template>
      <template v-else>
        <p class="title">{{ mode === 'signup' ? '회원가입' : '로그인' }}</p>
        <p class="mail">데모 계정으로 보고 있어요. 로그인하면 내 일정이 따로 저장돼요.</p>
        <AuthForm @mode="m => (mode = m)" @done="router.go(0)" />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown, Camera, Bookmark, ImagePlus, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { fileToDataUrl } from '../utils/image'
import AuthForm from './AuthForm.vue'
import SceneArt from './SceneArt.vue'

defineProps({ open: Boolean })
const emit = defineEmits(['toggle', 'close'])
const auth = useAuthStore(), router = useRouter(), mode = ref('login'), err = ref('')

async function onPhoto(e) {
  const file = e.target.files?.[0]; e.target.value = ''
  if (!file) return
  err.value = ''
  try { await auth.update({ photo: await fileToDataUrl(file, 600) }) } catch (x) { err.value = x.message }
}
function logout() { auth.logout(); emit('close'); router.push('/') }
</script>

<style scoped>
.um { position: relative; }
.who { display: flex; align-items: center; gap: 10px; padding: 4px 10px 4px 4px; border-radius: 999px; background: none; color: var(--ink); font-weight: 600; }
.who:hover { background: var(--hover); }
.avatar { width: 34px; height: 34px; }
.big .avatar { width: 48px; height: 48px; }
.avatar img, .avatar :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.greet { font-size: 14px; }
.chev { color: var(--muted); }
.menu { position: absolute; right: 0; top: 54px; width: 300px; padding: 10px; background: #fff; border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow-lg); display: grid; gap: 2px; }
.me { display: flex; align-items: center; gap: 12px; padding: 8px 8px 12px; margin-bottom: 4px; border-bottom: 1px solid var(--line); }
.me > span:last-child { display: grid; min-width: 0; }
.me small { font-size: 12.5px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; }
.title { margin: 6px 6px 0; font-weight: 700; }
.mail { margin: 2px 6px 10px; font-size: 13px; color: var(--muted); }
.item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 12px; background: none; color: var(--ink); text-align: left; font-weight: 500; font-size: 14px; text-decoration: none; cursor: pointer; }
.item:hover { background: var(--hover); }
.item.out { color: var(--i-red); }
.err { margin: 4px 8px 0; color: var(--i-red); font-size: 13px; }
@media (max-width: 760px) {
  .greet, .chev { display: none; }
  .menu { position: fixed; left: 12px; right: 12px; top: 64px; width: auto; }
}
</style>
