<template>
  <RouterView v-if="route.meta.bare" :key="route.fullPath" />
  <template v-else>
    <!-- 좁은 화면: 상단 헤더, 넓은 화면: 왼쪽 사이드바 -->
    <AppHeader v-if="isMobile" />
    <div class="app" :class="{ side: !isMobile }">
      <AppSidebar v-if="!isMobile" />
      <div class="main">
        <HeroCollage v-if="route.meta.hero" />
        <div v-else-if="!isMobile && !route.meta.banner" class="topline"></div>
        <FloatUser v-if="!isMobile" :hero="!!(route.meta.hero || route.meta.banner)" />
        <main class="shell" :class="{ flush: route.meta.banner }"><RouterView :key="route.fullPath" /></main>
        <AppFooter />
      </div>
    </div>
  </template>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import AppFooter from './components/AppFooter.vue'
import HeroCollage from './components/HeroCollage.vue'
import FloatUser from './components/FloatUser.vue'

const route = useRoute()
const mq = window.matchMedia('(max-width: 1000px)')
const isMobile = ref(mq.matches)
const onMq = e => (isMobile.value = e.matches)
onMounted(() => mq.addEventListener('change', onMq))
onBeforeUnmount(() => mq.removeEventListener('change', onMq))
</script>

<style scoped>
.app.side { display: grid; grid-template-columns: 270px minmax(0, 1fr); }
.main { position: relative; min-width: 0; min-height: 100vh; display: flex; flex-direction: column; }
.topline { height: 64px; }
.shell { flex: 1; width: 100%; max-width: 1320px; margin: 0 auto; padding: 24px 32px 64px; }
.shell.flush { max-width: none; padding: 0; }   /* 홈: 배너가 화면 폭 전체, 본문 폭은 HomeView 안에서 맞춤 */
@media (max-width: 1000px) { .shell { padding: 20px 16px 48px; } .shell.flush { padding: 0; } }
</style>
