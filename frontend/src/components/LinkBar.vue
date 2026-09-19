<template>
  <form class="linkbar callout" @submit.prevent="submit">
    <span class="ic" aria-hidden="true">🔗</span>
    <div class="body">
      <strong class="serif">SNS 링크 붙여넣기</strong>
      <small>인스타그램·블로그·기사 링크를 넣으면 내용·대상·자격·기간을 공식 공고와 비교해드려요.</small>
      <div class="row">
        <input v-model="url" type="url" placeholder="https://www.instagram.com/p/..." aria-label="SNS 링크" />
        <button :disabled="!validUrl || running">{{ running ? '분석 중…' : '가져오기' }}</button>
      </div>
      <div class="foot">
        <span v-if="running" class="status"><i class="spin"></i>{{ job.message || '링크를 읽는 중' }}</span>
        <span v-else-if="error" class="status err">{{ error }}</span>
        <span v-else-if="notice" class="status ok">✓ {{ notice }}</span>
        <template v-else>
          <span class="muted">예시로 해보기</span>
          <button v-for="s in SAMPLES" :key="s.label" type="button" class="sample" @click="url = s.url">{{ s.label }}</button>
          <RouterLink to="/upload" class="muted up">스크린샷으로 올리기</RouterLink>
        </template>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { createShare } from '../api/nexto'
import { useJobStore } from '../stores/job'

// category: 카테고리 페이지에서 넣으면 검토 화면의 저장 카테고리 기본값
const props = defineProps({ category: String, notice: String })
// 데모 모드에서 예시 데이터로 연결되는 샘플 링크
const SAMPLES = [
  { label: '청년 적금', url: 'https://www.instagram.com/p/NEXTO_SAMPLE_FINANCE/' },
  { label: '청년 월세 지원', url: 'https://www.instagram.com/p/NEXTO_SAMPLE_HOUSING/' },
  { label: '가을 축제', url: 'https://www.instagram.com/p/NEXTO_SAMPLE_FESTIVAL/' }
]
const router = useRouter(), job = useJobStore()
const url = ref(''), running = ref(false), error = ref('')
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
  else if (s === 'COMPLETED') router.push({ path: `/review/${job.result.share_id}`, query: props.category ? { category: props.category } : {} })
})
onUnmounted(() => job.stop?.())
</script>

<style scoped>
.linkbar { align-items: flex-start; }
.ic { font-size: 20px; line-height: 1.3; }
.body { flex: 1; min-width: 0; }
.body strong { display: block; font-size: 16px; }
.body small { display: block; color: var(--muted); font-size: 13px; margin: 2px 0 10px; }
.row { display: flex; gap: 8px; }
.row input { background: #fff; }
.row button { flex: none; padding: 0 18px; }
.foot { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 10px; font-size: 13px; min-height: 26px; }
.muted { color: var(--faint); }
.sample { padding: 2px 9px; border-radius: 4px; background: #fff; color: var(--ink); border: 1px solid var(--line); font-size: 12.5px; font-weight: 400; }
.sample:hover { background: var(--hover); }
.up { margin-left: auto; }
.status { display: inline-flex; align-items: center; gap: 8px; color: var(--muted); }
.status.err { color: var(--i-red); }
.status.ok { color: var(--mint-ink); }
.spin { width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--line); border-top-color: var(--blue); animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 560px) { .row { flex-direction: column; } .row button { height: 38px; } .up { margin-left: 0; } }
</style>
