import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 랜딩·로그인은 누구나, 나머지는 세션(로그인 또는 데모) 필요
const routes = [
  { path: '/', component: () => import('../views/LandingView.vue'), meta: { bare: true, public: true } },
  { path: '/login', redirect: to => ({ path: '/', query: to.query, hash: '#login' }) },
  { path: '/home', component: () => import('../views/HomeView.vue'), meta: { hero: true } },
  { path: '/category/:key', component: () => import('../views/CategoryView.vue') },
  { path: '/upload', component: () => import('../views/UploadView.vue') },
  { path: '/analyze/:jobId', component: () => import('../views/AnalyzeView.vue') },
  { path: '/review/:shareId', component: () => import('../views/ReviewView.vue'), meta: { hero: true } },
  { path: '/calendar', component: () => import('../views/CalendarView.vue'), meta: { hero: true } },
  { path: '/map', component: () => import('../views/MapView.vue'), meta: { hero: true } },
  { path: '/liked', component: () => import('../views/LikedView.vue'), meta: { hero: true } },
  { path: '/items', component: () => import('../views/ItemListView.vue') },
  { path: '/items/:itemId', component: () => import('../views/ItemDetailView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes, scrollBehavior: () => ({ top: 0 }) })

router.beforeEach(async to => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.loggedIn) return { path: '/', query: { next: to.fullPath }, hash: '#login' }
  try { await auth.fetchMe() } catch { return { path: '/', query: { next: to.fullPath }, hash: '#login' } }
  return true
})

export default router
