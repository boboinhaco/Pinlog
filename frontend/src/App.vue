<template>
  <RouterView v-if="route.meta.bare" :key="route.fullPath" />
  <template v-else>
    <AppHeader />
    <HeroCollage v-if="route.meta.hero" />
    <main class="shell"><RouterView :key="route.fullPath" /></main>
    <AppFooter />
  </template>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import HeroCollage from './components/HeroCollage.vue'

const route = useRoute()
</script>

<style scoped>
.shell { max-width: 1280px; margin: 0 auto; padding: 28px 32px 64px; min-height: calc(100vh - 68px); }
@media (max-width: 760px) { .shell { padding: 20px 16px 48px; } }
</style>
