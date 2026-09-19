<template>
  <header v-if="!route.meta.bare" class="topbar">
    <nav class="crumb">
      <RouterLink to="/home" class="brand"><SproutIcon :size="18" />NEXTO</RouterLink>
      <template v-if="route.meta.crumb"><span class="sep">/</span><span>{{ route.meta.crumb }}</span></template>
    </nav>
    <nav class="links">
      <RouterLink v-for="n in NAV" :key="n.to" :to="n.to">{{ n.label }}</RouterLink>
    </nav>
    <div class="me">
      <span v-if="auth.isDemo" class="tag tone-yellow">데모</span>
      <span class="avatar" :title="auth.user?.email">
        <img v-if="auth.user?.photo" :src="auth.user.photo" alt="" />
        <template v-else>{{ (auth.displayName || 'N').slice(0, 1) }}</template>
      </span>
    </div>
  </header>
  <main :class="{ padded: !route.meta.bare && !route.meta.cover }"><RouterView :key="route.fullPath" /></main>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import SproutIcon from './components/SproutIcon.vue'

const NAV = [{ to: '/home', label: '홈' }, { to: '/calendar', label: '일정' }, { to: '/map', label: '지도' }, { to: '/items', label: '저장됨' }]
const route = useRoute(), auth = useAuthStore()
</script>

<style scoped>
.topbar { position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; gap: 16px; height: 45px; padding: 0 14px; background: rgba(255, 255, 255, .96); backdrop-filter: blur(6px); border-bottom: 1px solid var(--line); font-size: 14px; }
.crumb { display: flex; align-items: center; gap: 6px; min-width: 0; flex: 1; color: var(--muted); }
.brand { display: flex; align-items: center; gap: 6px; padding: 2px 6px; border-radius: 4px; color: var(--ink); text-decoration: none; font-family: var(--serif); font-weight: 700; }
.brand:hover { background: var(--hover); }
.sep { color: var(--faint); }
.crumb > span:last-child { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.links { display: flex; gap: 2px; }
.links a { padding: 3px 9px; border-radius: 4px; color: var(--muted); text-decoration: none; }
.links a:hover { background: var(--hover); }
.links a.router-link-active { color: var(--ink); background: var(--hover); }
.me { flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 8px; }
.avatar { width: 26px; height: 26px; border-radius: 50%; overflow: hidden; display: grid; place-items: center; background: var(--mint); color: var(--mint-ink); font-size: 12px; font-weight: 700; }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
@media (max-width: 640px) {
  .topbar { gap: 8px; }
  .crumb .sep, .crumb > span:last-child { display: none; }
  .links a { padding: 3px 6px; }
  .me .tag { display: none; }
  .me { flex: none; }
}
</style>
