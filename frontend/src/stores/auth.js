import { defineStore } from 'pinia'
import * as api from '../api/nexto'

// 로그인 세션 + 내 프로필(아치 사진·커버·퀵노트)
export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('nexto_token'), user: null }),
  getters: {
    loggedIn: s => !!s.token,
    isDemo: s => !!s.user?.is_demo,
    displayName: s => s.user?.name ?? ''
  },
  actions: {
    _set({ token, user }) {
      this.token = token; this.user = user
      localStorage.setItem('nexto_token', token)
    },
    async demo() { this._set(await api.demoLogin()) },
    async login(email, password) { this._set(await api.login({ email, password })) },
    async signup(email, password, name) { this._set(await api.signup({ email, password, name })) },
    async fetchMe() { if (this.token && !this.user) this.user = await api.getMe() },
    async update(body) { this.user = await api.updateMe(body) },
    logout() {
      this.token = null; this.user = null
      localStorage.removeItem('nexto_token'); localStorage.removeItem('nexto_last_items')
    }
  }
})
