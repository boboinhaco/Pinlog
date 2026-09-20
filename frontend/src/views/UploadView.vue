<template>
  <section class="up">
    <PageHero align="left" back="/home" title="스크린샷으로 올리기"
              sub="게시물을 장별로 캡처해 올리면 사진 속 글자까지 꼼꼼히 읽어요. 캡션을 함께 넣으면 더 정확해요."
              doodle="사진 속 글자까지<br>놓치지 않게!" />

    <!-- 3단계 안내 -->
    <ol class="how">
      <li v-for="(h, i) in HOW" :key="h.title" :style="{ '--i': i }">
        <span class="n">{{ i + 1 }}</span>
        <span class="ic"><component :is="h.icon" :size="18" /></span>
        <span class="tx"><b>{{ h.title }}</b><small>{{ h.desc }}</small></span>
      </li>
    </ol>

    <div class="cols">
      <!-- 캡처 사진 -->
      <section class="card">
        <div class="hd"><h2 class="section-title"><ImageUp :size="20" />캡처 사진</h2><small class="muted" :class="{ full: files.length >= MAX }">{{ files.length }} / {{ MAX }}장</small></div>
        <label class="drop" :class="{ over, has: files.length }" @dragover.prevent="over = true" @dragleave="over = false" @drop.prevent="onDrop">
          <input type="file" multiple accept="image/jpeg,image/png,image/webp" hidden :disabled="files.length >= MAX" @change="onPick" />
          <template v-if="!files.length">
            <span class="cloud"><CloudUpload :size="30" :stroke-width="1.8" /></span>
            <b>사진을 끌어다 놓거나 눌러서 선택</b>
            <small>JPG · PNG · WEBP, 장당 6MB 이하 · 최대 {{ MAX }}장</small>
          </template>
          <ul v-else class="thumbs">
            <li v-for="(f, i) in files" :key="f.url" class="th">
              <img :src="f.url" alt="" />
              <i class="idx">{{ i + 1 }}</i>
              <button type="button" class="rm" aria-label="이 사진 빼기" @click.prevent.stop="remove(i)"><X :size="14" :stroke-width="2.6" /></button>
            </li>
            <li v-if="files.length < MAX" class="th add"><Plus :size="22" /><small>추가</small></li>
          </ul>
        </label>
        <p v-if="fileError" class="err"><CircleAlert :size="15" />{{ fileError }}</p>
        <p class="hint"><Lightbulb :size="14" />게시물 순서대로 올리면 여러 장에 나뉜 정보도 이어서 읽어요.</p>
      </section>

      <!-- 캡션 · 링크 · 실행 -->
      <section class="card form">
        <div class="hd"><h2 class="section-title"><FileText :size="20" />캡션 · 텍스트 <small>선택</small></h2><small class="muted">{{ text.length.toLocaleString() }} / 3,000</small></div>
        <textarea v-model="text" rows="7" maxlength="3000" placeholder="캡션이나 DM 내용을 붙여넣어 주세요. 사진만 올려도 괜찮아요."></textarea>
        <label class="url"><Link2 :size="16" /><input v-model="url" type="url" placeholder="원본 링크 (선택 · 저장한 뒤 다시 열어보는 용도)" aria-label="원본 링크" /></label>
        <p v-if="error" class="err"><CircleAlert :size="15" />{{ error.message }}</p>
        <div class="acts">
          <button class="primary go" :disabled="loading || !canSubmit" @click="submit">
            <LoaderCircle v-if="loading" :size="18" class="spin" /><Sparkles v-else :size="18" />{{ loading ? '올리는 중…' : '분석 시작하기' }}
          </button>
          <button type="button" class="ghost" @click="loadSample"><Wand :size="16" />샘플 텍스트 넣기</button>
        </div>
        <p class="note">{{ canSubmit ? `${inputLabel}로 분석해요. 보통 20초 안팎이 걸려요.` : '사진이나 텍스트 중 하나는 있어야 해요.' }}</p>
      </section>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Camera, ImageUp, Sparkles, CloudUpload, X, Plus, Lightbulb, FileText, Link2, CircleAlert, LoaderCircle, Wand } from 'lucide-vue-next'
import { createShare } from '../api/nexto'
import PageHero from '../components/PageHero.vue'

const MAX = 5, MAX_BYTES = 6_000_000
const HOW = [
  { icon: Camera, title: '게시물을 장별로 캡처', desc: '여러 장이면 한 장씩, 최대 5장' },
  { icon: ImageUp, title: '여기에 올리기', desc: '끌어다 놓거나 눌러서 선택' },
  { icon: Sparkles, title: '확인하고 저장', desc: 'AI가 정리한 내용을 검토해요' }
]
const router = useRouter()
const files = ref([]), text = ref(''), url = ref(useRoute().query.url ?? ''), loading = ref(false), error = ref(null), fileError = ref(''), over = ref(false)
const canSubmit = computed(() => files.value.length > 0 || text.value.trim().length > 0)
// "사진 2장으로" / "사진 2장과 텍스트로" / "텍스트로"
const inputLabel = computed(() => {
  const n = files.value.length, t = text.value.trim().length > 0
  return n && t ? `사진 ${n}장과 텍스트` : n ? `사진 ${n}장으` : '텍스트'
})

// 파일 추가: 이미지만, 6MB 이하, 5장까지 (미리보기용 object URL은 뺄 때 해제)
function add(list) {
  fileError.value = ''
  const room = MAX - files.value.length
  const imgs = [...list].filter(f => f.type.startsWith('image/'))
  const big = imgs.filter(f => f.size > MAX_BYTES)
  const ok = imgs.filter(f => f.size <= MAX_BYTES)
  if (big.length) fileError.value = `6MB가 넘는 사진 ${big.length}장은 뺐어요.`
  else if (ok.length > room) fileError.value = `최대 ${MAX}장까지만 올릴 수 있어 ${ok.length - room}장은 뺐어요.`
  files.value.push(...ok.slice(0, room).map(file => ({ file, url: URL.createObjectURL(file) })))
}
const onPick = e => { add(e.target.files); e.target.value = '' }
const onDrop = e => { over.value = false; add(e.dataTransfer.files) }
function remove(i) { URL.revokeObjectURL(files.value[i].url); files.value.splice(i, 1); fileError.value = '' }
onUnmounted(() => files.value.forEach(f => URL.revokeObjectURL(f.url)))

// 데모용 샘플 입력 (fixtures/demo와 키워드 일치)
const loadSample = () => (text.value = '서울 청년 주거비 지원! 19~34세 서울 거주 청년이면 월 최대 20만원 지원. 9월까지 신청하세요 🏠')

async function submit() {
  loading.value = true; error.value = null
  const fd = new FormData()
  files.value.forEach(f => fd.append('images', f.file))
  fd.append('text', text.value); fd.append('original_url', url.value.trim())
  try {
    const { job_id } = await createShare(fd)
    router.push(`/analyze/${job_id}`)
  } catch (e) { error.value = e } finally { loading.value = false }
}
</script>

<style scoped>
.up { display: grid; gap: 16px; }
.how { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 0; padding: 0; list-style: none; }
.how li { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 14px; background: #fff; animation: rise .5s ease both; animation-delay: calc(var(--i) * 90ms); }
.how .n { flex: none; display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: var(--cta); color: #fff; font-size: 12px; font-weight: 700; }
.how .ic { flex: none; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: var(--grad-soft); color: var(--accent-deep); }
.how .tx { display: grid; min-width: 0; }
.how b { font-size: 14px; }
.how small { font-size: 12px; color: var(--muted); }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }
.cols { display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; align-items: start; }
.card { margin: 0; padding: 20px 22px; }
.hd { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 12px; }
.hd .section-title { margin: 0; }
.muted { font-size: 13px; color: var(--muted); }
.muted.full { color: var(--accent); font-weight: 600; }
/* 드롭 영역 */
.drop { display: grid; place-items: center; gap: 6px; min-height: 260px; padding: 20px; border: 2px dashed var(--line-strong); border-radius: 16px; background: var(--soft); text-align: center; cursor: pointer; transition: border-color .15s, background .15s, transform .15s; }
.drop:hover, .drop.over { border-color: var(--accent); background: var(--accent-soft); }
.drop.over { transform: scale(1.01); }
.drop.has { display: block; min-height: 0; padding: 14px; border-style: solid; border-color: var(--line); background: #fff; cursor: default; }
.drop.has:hover { border-color: var(--line); background: #fff; }
.drop.has.over { border-color: var(--accent); background: var(--accent-soft); }
.cloud { display: grid; place-items: center; width: 64px; height: 64px; border-radius: 50%; background: var(--grad-soft); color: var(--accent-deep); animation: bob 2.2s ease-in-out infinite; }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.drop b { font-size: 15px; }
.drop small { font-size: 12.5px; color: var(--muted); }
.thumbs { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin: 0; padding: 0; list-style: none; }
.th { position: relative; aspect-ratio: 4 / 5; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); background: #fff; animation: pop .35s ease both; }
.th img { width: 100%; height: 100%; object-fit: cover; display: block; }
.idx { position: absolute; left: 8px; top: 8px; display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: rgba(0, 0, 0, .55); color: #fff; font-style: normal; font-size: 12px; font-weight: 700; }
.rm { position: absolute; right: 6px; top: 6px; width: 26px; height: 26px; padding: 0; border-radius: 50%; display: grid; place-items: center; background: rgba(255, 255, 255, .95); color: var(--ink); box-shadow: 0 1px 4px rgba(0, 0, 0, .18); }
.rm:hover { color: var(--i-red); }
.th.add { display: grid; place-items: center; align-content: center; gap: 2px; border: 2px dashed var(--line-strong); color: var(--muted); cursor: pointer; }
.th.add:hover { border-color: var(--accent); color: var(--accent); }
@keyframes pop { from { opacity: 0; transform: scale(.85); } }
.hint { display: flex; align-items: center; gap: 6px; margin: 10px 0 0; font-size: 12.5px; color: var(--muted); }
.err { display: flex; align-items: center; gap: 6px; margin: 10px 0 0; font-size: 13px; color: var(--i-red); }
/* 폼 */
.form textarea { resize: vertical; min-height: 150px; line-height: 1.6; }
.url { display: flex; align-items: center; gap: 8px; margin-top: 10px; padding: 0 12px; border: 1px solid var(--line-strong); border-radius: 12px; background: #fff; color: var(--muted); }
.url input { border: 0; padding: 10px 0; }
.url input:focus { box-shadow: none; }
.acts { display: grid; grid-template-columns: 1fr auto; gap: 10px; margin-top: 14px; }
.acts button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; height: 48px; border-radius: 14px; font-size: 15px; }
.note { margin: 10px 0 0; font-size: 12.5px; color: var(--muted); }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
@media (max-width: 640px) { .how { grid-template-columns: 1fr; } .acts { grid-template-columns: 1fr; } }
</style>
