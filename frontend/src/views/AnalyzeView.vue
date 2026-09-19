<template>
  <section>
    <h1 class="page-title">AI 분석 중</h1>
    <ol class="steps">
      <li v-for="s in STAGES" :key="s" :class="{ active: s === job.stage, done: isDone(s) }">{{ LABEL[s] }}</li>
    </ol>
    <p>{{ job.message }}</p>
    <div v-if="job.status === 'FAILED'" class="card">
      <p style="color:#d2323f">{{ job.error?.message }}</p>
      <button v-if="job.error?.retryable" @click="job.retry()">실패한 단계부터 다시 시도</button>
      <RouterLink to="/home" style="margin-left:8px">홈으로 돌아가기</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useJobStore } from '../stores/job'

const STAGES = ['UNDERSTAND', 'EXTRACT', 'NORMALIZE', 'SEARCH', 'VERIFY']
const LABEL = { UNDERSTAND: '이해', EXTRACT: '추출', NORMALIZE: '정리', SEARCH: '공식 검색', VERIFY: '검증' }
const route = useRoute(), router = useRouter(), job = useJobStore()
job.subscribe(route.params.jobId)
const isDone = s => STAGES.indexOf(s) < STAGES.indexOf(job.stage) || job.status === 'COMPLETED'

// 완료 시 검토 화면으로
watch(() => job.status, v => { if (v === 'COMPLETED') router.push(`/review/${job.result.share_id}`) })
onUnmounted(() => job.stop?.())
</script>

<style scoped>
.steps { display: flex; gap: 8px; list-style: none; padding: 0; flex-wrap: wrap; }
.steps li { padding: 6px 12px; border-radius: 6px; background: #eef0f7; font-size: 14px; }
.steps li.active { background: var(--primary); color: #fff; }
.steps li.done { background: #d8f2e1; }
</style>
