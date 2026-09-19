<template>
  <section>
    <h1 class="page-title">스크린샷·텍스트로 올리기</h1>
    <p class="evidence">스크린샷 1~5장과 캡션 텍스트를 함께 넣으면 정확도가 올라가요.</p>
    <input type="file" multiple accept="image/jpeg,image/png,image/webp" @change="onFiles" />
    <p v-if="files.length" class="evidence">{{ files.length }}장 선택됨</p>
    <textarea v-model="text" placeholder="캡션/DM 텍스트 붙여넣기 (최대 3,000자)" rows="6" maxlength="3000"></textarea>
    <input v-model="url" placeholder="원본 링크 (선택, 저장용)" />
    <div style="display:flex; gap:8px;">
      <button :disabled="loading || (!files.length && !text.trim())" @click="submit">분석 시작</button>
      <button class="ghost" @click="loadSample">샘플 불러오기</button>
    </div>
    <p v-if="error" style="color:#d2323f">{{ error.message }}</p>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createShare } from '../api/nexto'

const router = useRouter()
const files = ref([]), text = ref(''), url = ref(useRoute().query.url ?? ''), loading = ref(false), error = ref(null)
const onFiles = e => (files.value = [...e.target.files].slice(0, 5))

// 데모용 샘플 입력 (fixtures/demo와 키워드 일치)
const loadSample = () => (text.value = '서울 청년 주거비 지원! 19~34세 서울 거주 청년이면 월 최대 20만원 지원. 9월까지 신청하세요 🏠')

async function submit() {
  loading.value = true; error.value = null
  const fd = new FormData()
  files.value.forEach(f => fd.append('images', f))
  fd.append('text', text.value); fd.append('original_url', url.value)
  try {
    const { job_id } = await createShare(fd)
    router.push(`/analyze/${job_id}`)
  } catch (e) { error.value = e } finally { loading.value = false }
}
</script>

<style scoped>
section { display: grid; gap: 12px; }
</style>
