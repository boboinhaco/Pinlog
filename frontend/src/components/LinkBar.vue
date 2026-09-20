<template>
  <div class="lb">
    <form class="bar" @submit.prevent="submit">
      <span class="ic"><Link2 :size="22" :stroke-width="2.2" /></span>
      <input v-model="url" type="url" placeholder="Instagram, 블로그, YouTube 등의 링크를 붙여넣어 주세요." aria-label="SNS 링크" />
      <button class="primary" :disabled="!validUrl || running">
        <LoaderCircle v-if="running" :size="18" class="spin" /><Sparkles v-else :size="18" />
        {{ running ? '분석 중…' : buttonLabel }} <ArrowRight v-if="!running" :size="18" />
      </button>
    </form>
    <div class="foot" role="status">
      <span v-if="running" class="st"><span class="steps"><i v-for="s in STAGES" :key="s" :class="{ on: STAGES.indexOf(s) <= STAGES.indexOf(job.stage) }"></i></span>{{ job.message || '링크를 읽는 중이에요' }} · 공식 공고와 비교까지 20초 정도 걸려요</span>
      <span v-else-if="error" class="st err"><CircleAlert :size="16" />{{ error }}</span>
      <template v-else-if="!compact">
        <span v-if="notice" class="st ok"><CircleCheck :size="16" />{{ notice }}</span>
        <span class="muted">예시 링크로 먼저 체험해보세요!</span>
        <button v-for="s in SAMPLES" :key="s.label" type="button" class="sample" @click="url = s.url">
          <span class="dot" :style="{ background: s.color }"><component :is="s.icon" :size="12" :stroke-width="2.6" color="#fff" /></span>{{ s.label }}
        </button>
        <RouterLink to="/upload" class="muted up"><ImagePlus :size="15" />스크린샷으로 올리기</RouterLink>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Link2, Sparkles, ArrowRight, LoaderCircle, CircleAlert, CircleCheck, ImagePlus, Instagram, Youtube, FileText, ShoppingBag } from 'lucide-vue-next'
import { createShare } from '../api/nexto'
import { useJobStore } from '../stores/job'

// category: 카테고리 페이지에서 넣으면 검토 화면의 저장 카테고리 기본값
const props = defineProps({ category: String, notice: String, buttonLabel: { type: String, default: '링크 분석하기' }, query: Object, initialUrl: String, compact: Boolean })
// 데모 모드에서 예시 데이터로 연결되는 샘플 링크
const SAMPLES = [
  { label: '인스타그램 예시', url: 'https://www.instagram.com/p/PINLOG_SAMPLE_FESTIVAL/', color: 'var(--grad)', icon: Instagram },
  { label: 'YouTube 예시', url: 'https://www.youtube.com/watch?v=PINLOG_SAMPLE_FINANCE', color: '#ff0033', icon: Youtube },
  { label: '블로그 예시', url: 'https://blog.naver.com/pinlog/PINLOG_SAMPLE_HOUSING', color: '#03c75a', icon: FileText },
  { label: '추천템 예시', url: 'https://www.instagram.com/p/PINLOG_SAMPLE_PRODUCT/', color: '#4f5bd5', icon: ShoppingBag }
]
const STAGES = ['UNDERSTAND', 'EXTRACT', 'NORMALIZE', 'SEARCH', 'VERIFY']
const router = useRouter(), job = useJobStore()
const url = ref(props.initialUrl ?? ''), running = ref(false), error = ref('')
const validUrl = computed(() => /^https?:\/\/\S+\.\S+/.test(url.value.trim()))

async function submit() {
  running.value = true; error.value = ''
  const fd = new FormData(); fd.append('original_url', url.value.trim())
  try { job.subscribe((await createShare(fd)).job_id) } catch (e) { running.value = false; error.value = e.message }
}
// 분석이 끝나면 검토 화면으로 (저장은 사용자가 확인한 뒤에)
watch(() => job.status, s => {
  if (!running.value) return
  if (s === 'FAILED') { running.value = false; error.value = job.error?.message ?? '다시 시도해 주세요.' }
  else if (s === 'COMPLETED') router.push({ path: `/review/${job.result.share_id}`, query: { ...(props.category ? { category: props.category } : {}), ...props.query } })
})
onUnmounted(() => job.stop?.())
</script>

<style scoped>
.bar { display: flex; align-items: center; gap: 12px; padding: 8px 8px 8px 10px; background: #fff; border: 1px solid var(--line); border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, .06); transition: box-shadow .2s, border-color .2s; }
.bar:focus-within { border-color: #f3b4d2; box-shadow: 0 0 0 4px var(--focus), 0 10px 30px rgba(0, 0, 0, .06); }
.ic { flex: none; display: grid; place-items: center; width: 42px; height: 42px; border-radius: 14px; background: var(--grad-soft); color: var(--accent); }
.bar input { flex: 1; min-width: 0; border: 0; padding: 12px 0; font-size: 16px; background: none; box-shadow: none; }
.bar input:focus { outline: none; box-shadow: none; }
.bar button { flex: none; display: flex; align-items: center; gap: 8px; height: 52px; padding: 0 24px; border-radius: 14px; font-size: 16px; }
.foot:empty { display: none; }
.foot { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 8px 10px; margin-top: 18px; min-height: 36px; font-size: 13.5px; }
.muted { color: var(--muted); }
.sample { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px 6px 8px; border-radius: 999px; background: #fff; color: var(--ink); border: 1px solid var(--line-strong); font-size: 13px; font-weight: 600; }
.sample:hover { background: var(--hover); }
.dot { display: grid; place-items: center; width: 22px; height: 22px; border-radius: 7px; }
.up { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; text-decoration: none; }
.up:hover { color: var(--ink); }
.st { display: inline-flex; align-items: center; gap: 8px; color: var(--ink-2); }
.st.err { color: var(--i-red); }
.st.ok { color: var(--mint-ink); flex-basis: 100%; justify-content: center; }
.steps { display: inline-flex; gap: 4px; }
.steps i { width: 18px; height: 4px; border-radius: 2px; background: var(--line-strong); }
.steps i.on { background: var(--cta); }
@media (max-width: 640px) {
  .bar { flex-wrap: wrap; padding: 10px 12px; }
  .bar input { flex-basis: calc(100% - 44px); }
  .bar button { width: 100%; justify-content: center; height: 48px; }
}
</style>
