import axios from 'axios'

// envelope { success, data, error } 처리, JWT 자동 첨부, 세션 만료(401)면 토큰 지우고 첫 화면으로
const client = axios.create({ baseURL: '/api' })
client.interceptors.request.use(cfg => {
  const token = localStorage.getItem('nexto_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
client.interceptors.response.use(res => res.data.data, err => {
  const error = err.response?.data?.error ?? { code: 'NETWORK', message: '서버에 연결할 수 없어요.', retryable: true }
  if (err.response?.status === 401 && !err.config.url.startsWith('/auth/login')) {
    localStorage.removeItem('nexto_token')
    if (location.pathname !== '/' && location.pathname !== '/login') location.assign('/login?expired=1')
  }
  return Promise.reject(error)
})

export default client
