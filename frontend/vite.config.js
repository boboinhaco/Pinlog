import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// /api는 FastAPI로 프록시, PWA 매니페스트 포함
export default defineConfig({
  plugins: [vue(), VitePWA({ registerType: 'autoUpdate', manifest: { name: 'Pinlog 핀로그', short_name: 'Pinlog', theme_color: '#ffffff', background_color: '#fafafa', display: 'standalone', icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }] } })],
  server: { port: 5173, proxy: { '/api': { target: process.env.VITE_API_URL || 'http://localhost:8000', changeOrigin: true } } }
})
