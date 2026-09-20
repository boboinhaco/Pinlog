// 원본 링크 → SNS 출처 (좋아요한 콘텐츠 필터·배지용)
export const SOURCES = [
  { key: 'instagram', label: 'Instagram', color: 'linear-gradient(45deg,#f9b233,#e1306c,#833ab4)', test: h => /instagram\.com$/.test(h) },
  { key: 'youtube', label: 'YouTube', color: '#ff0033', test: h => /(youtube\.com|youtu\.be)$/.test(h) },
  { key: 'blog', label: '블로그', color: '#03c75a', test: h => /(blog\.naver\.com|tistory\.com|brunch\.co\.kr|velog\.io|medium\.com)$/.test(h) || h.startsWith('blog.') },
  { key: 'etc', label: '기타', color: '#6b7489', test: () => true }
]
export function sourceOf(url) {
  if (!url) return { key: 'manual', label: '직접 추가', color: '#6b7489' }
  let host = ''
  try { host = new URL(url).hostname.replace(/^www\.|^m\./, '') } catch { /* 잘못된 주소는 기타 */ }
  return SOURCES.find(s => s.test(host))
}
