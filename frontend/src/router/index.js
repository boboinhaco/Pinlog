import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 랜딩·로그인은 누구나, 나머지는 세션(로그인 또는 데모) 필요
const routes = [
  { path: '/', component: () => import('../views/LandingView.vue'), meta: { bare: true, public: true } },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { bare: true, public: true } },
  { path: '/home', component: () => import('../views/HomeView.vue'), meta: { cover: true } },
  { path: '/category/:key', component: () => import('../views/CategoryView.vue'), meta: { cover: true, crumb: '카테고리' } },
  { path: '/upload', component: () => import('../views/UploadView.vue'), meta: { crumb: '스크린샷으로 올리기' } },
  { path: '/analyze/:jobId', component: () => import('../views/AnalyzeView.vue'), meta: { crumb: '분석 중' } },
  { path: '/review/:shareId', component: () => import('../views/ReviewView.vue'), meta: { crumb: '확인하기' } },
  { path: '/calendar', component: () => import('../views/CalendarView.vue'), meta: { crumb: '일정' } },
  { path: '/map', component: () => import('../views/MapView.vue'), meta: { crumb: '지도' } },
  { path: '/items', component: () => import('../views/ItemListView.vue'), meta: { crumb: '저장됨' } },
  { path: '/items/:itemId', component: () => import('../views/ItemDetailView.vue'), meta: { crumb: '상세' } },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes, scrollBehavior: () => ({ top: 0 }) })

router.beforeEach(async to => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.loggedIn) return { path: '/login', query: { next: to.fullPath } }
  try { await auth.fetchMe() } catch { return { path: '/login', query: { next: to.fullPath } } }
  return true
})

export default router
