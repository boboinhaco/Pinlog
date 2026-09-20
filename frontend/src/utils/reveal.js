// 스크롤로 보일 때 한 번만 나타나는 애니메이션 (v-reveal="지연ms")
const REDUCED = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

export const vReveal = {
  mounted(el, binding) {
    if (REDUCED) { el.classList.add('reveal-in'); return }
    el.classList.add('reveal')
    if (binding.value) el.style.transitionDelay = `${binding.value}ms`
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return
      el.classList.add('reveal-in')
      io.disconnect()
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' })
    io.observe(el)
    el._io = io
  },
  unmounted(el) { el._io?.disconnect() }
}
