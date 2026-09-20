<template>
  <section class="an">
    <div class="stage" :class="{ fail: failed, done: completed }">
      <!-- 떠다니는 배경 도형 -->
      <span v-for="n in 6" :key="n" class="blob" :class="`b${n}`" aria-hidden="true"></span>

      <!-- 현재 단계 아이콘 -->
      <div class="scene" aria-hidden="true">
        <span class="pulse"></span><span class="pulse p2"></span>
        <div class="orbit"><i></i><i></i><i></i></div>
        <div class="disc">
          <Transition name="swap" mode="out-in">
            <component :is="current.icon" :key="current.key" :size="46" :stroke-width="1.7" />
          </Transition>
        </div>
      </div>

      <Transition name="fade" mode="out-in">
        <h1 :key="current.key">{{ current.title }}</h1>
      </Transition>
      <p class="msg">{{ failed ? job.error?.message : completed ? '검토 화면으로 이동해요' : (job.message || current.hint) }}</p>

      <!-- 단계 진행 -->
      <ol class="steps" :aria-label="`분석 진행 ${doneCount}/${STAGES.length}`">
        <div class="bar"><div class="fill" :style="{ width: pct + '%' }"></div></div>
        <li v-for="s in STAGES" :key="s.key" :class="{ on: s.key === (job.stage ?? 'UNDERSTAND') && running, done: isDone(s.key) }">
          <span class="node"><Check v-if="isDone(s.key)" :size="16" :stroke-width="3" /><component v-else :is="s.icon" :size="16" /></span>
          <small>{{ s.label }}</small>
        </li>
      </ol>

      <div v-if="failed" class="fail-box">
        <button v-if="job.error?.retryable" @click="job.retry()"><RotateCcw :size="16" />실패한 단계부터 다시 시도</button>
        <RouterLink to="/upload" class="lnk">다시 올리기</RouterLink>
        <RouterLink to="/home" class="lnk">홈으로</RouterLink>
      </div>
      <template v-else>
        <Transition name="fade" mode="out-in">
          <p class="tip" :key="tipIdx"><Lightbulb :size="14" />{{ TIPS[tipIdx] }}</p>
        </Transition>
        <p class="eta"><Clock :size="13" />{{ elapsed }}초 지남 · 보통 20초 안팎이에요</p>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ScanEye, Sparkles, CalendarDays, Globe, ShieldCheck, PartyPopper, CircleAlert, Check, Lightbulb, Clock, RotateCcw } from 'lucide-vue-next'
import { useJobStore } from '../stores/job'

// 단계별 아이콘·제목 (메시지는 서버가 보내는 진행 문구 우선)
const STAGES = [
  { key: 'UNDERSTAND', label: '이해', icon: ScanEye, title: '게시물을 읽고 있어요', hint: '사진과 글을 꼼꼼히 살펴보는 중' },
  { key: 'EXTRACT', label: '추출', icon: Sparkles, title: '핵심 정보를 뽑고 있어요', hint: '일정·장소·상품을 찾는 중' },
  { key: 'NORMALIZE', label: '정리', icon: CalendarDays, title: '날짜와 장소를 정리해요', hint: '날짜 형식을 맞추고 주소를 찾는 중' },
  { key: 'SEARCH', label: '검색', icon: Globe, title: '인터넷에서 확인 중이에요', hint: '공식 출처와 상품 정보를 찾는 중' },
  { key: 'VERIFY', label: '검증', icon: ShieldCheck, title: '공식 정보와 비교하고 있어요', hint: '다른 점이 있는지 살펴보는 중' }
]
const DONE = { key: 'DONE', icon: PartyPopper, title: '분석 완료!' }
const FAIL = { key: 'FAIL', icon: CircleAlert, title: '분석을 마치지 못했어요' }
const TIPS = ['사진 속 글자도 같이 읽어요', '연도가 없는 날짜는 가장 가까운 미래로 맞추고 표시해 둬요', '공식 공고는 정부·공공기관·금융기관 사이트를 먼저 찾아요',
              '물건이 보이면 상품명을 검색으로 한 번 더 확인해요', '분석이 끝나면 저장 전에 직접 검토하고 고칠 수 있어요']

const route = useRoute(), router = useRouter(), job = useJobStore()
job.subscribe(route.params.jobId)
const running = computed(() => job.status === 'RUNNING'), failed = computed(() => job.status === 'FAILED'), completed = computed(() => job.status === 'COMPLETED')
const idx = computed(() => Math.max(0, STAGES.findIndex(s => s.key === job.stage)))
const current = computed(() => failed.value ? FAIL : completed.value ? DONE : STAGES[idx.value])
const isDone = key => completed.value || STAGES.findIndex(s => s.key === key) < idx.value
const doneCount = computed(() => STAGES.filter(s => isDone(s.key)).length)
const pct = computed(() => completed.value ? 100 : idx.value / (STAGES.length - 1) * 100)

// 기다리는 동안 팁 순환 + 경과 시간
const tipIdx = ref(0), elapsed = ref(0)
let tipTimer, clockTimer
onMounted(() => {
  tipTimer = setInterval(() => (tipIdx.value = (tipIdx.value + 1) % TIPS.length), 3200)
  clockTimer = setInterval(() => (elapsed.value += 1), 1000)
})
// 완료 배지를 잠깐 보여준 뒤 검토 화면으로
watch(() => job.status, v => { if (v === 'COMPLETED') setTimeout(() => router.push(`/review/${job.result.share_id}`), 800) })
onUnmounted(() => { clearInterval(tipTimer); clearInterval(clockTimer); job.stop?.() })
</script>

<style scoped>
.an { display: grid; place-items: center; min-height: 60vh; padding: 12px 0; }
.stage { position: relative; width: min(680px, 100%); padding: 44px 28px 30px; border: 1px solid var(--line); border-radius: 28px; background: #fff; box-shadow: var(--shadow); text-align: center; overflow: hidden; isolation: isolate; }
/* 배경 도형 */
.blob { position: absolute; z-index: -1; border-radius: 50%; filter: blur(18px); opacity: .55; animation: drift 7s ease-in-out infinite; }
.b1 { width: 160px; height: 160px; left: -40px; top: -30px; background: #feda75; }
.b2 { width: 120px; height: 120px; right: -30px; top: 40px; background: #f9c5da; animation-delay: -2s; }
.b3 { width: 90px; height: 90px; left: 12%; bottom: 30px; background: #d9c6f5; animation-delay: -4s; }
.b4 { width: 140px; height: 140px; right: 10%; bottom: -50px; background: #ffd9c2; animation-delay: -1s; }
.b5 { width: 60px; height: 60px; left: 40%; top: 10px; background: #c9d4fb; animation-delay: -3s; }
.b6 { width: 70px; height: 70px; right: 34%; bottom: 60px; background: #fbd3e6; animation-delay: -5s; }
@keyframes drift { 0%, 100% { transform: translate(0, 0) scale(1); } 50% { transform: translate(10px, -14px) scale(1.08); } }
/* 아이콘 장면 */
.scene { position: relative; width: 150px; height: 150px; margin: 0 auto 18px; display: grid; place-items: center; }
/* 퍼지는 그라데이션 원 (아이콘 원보다 뒤) */
.pulse { position: absolute; inset: 22px; z-index: 0; border-radius: 50%; background: var(--grad); animation: pulse 1.9s ease-out infinite; }
.pulse.p2 { animation-delay: .7s; }
@keyframes pulse { 0% { transform: scale(.85); opacity: .55; } 100% { transform: scale(1.45); opacity: 0; } }
.orbit { position: absolute; inset: 6px; border-radius: 50%; animation: spin 7s linear infinite; }
.orbit i { position: absolute; width: 12px; height: 12px; border-radius: 50%; background: var(--grad); box-shadow: 0 2px 6px rgba(0, 0, 0, .12); }
.orbit i:nth-child(1) { left: 50%; top: -6px; margin-left: -6px; }
.orbit i:nth-child(2) { right: 8px; bottom: 22px; width: 9px; height: 9px; }
.orbit i:nth-child(3) { left: 10px; bottom: 26px; width: 7px; height: 7px; }
@keyframes spin { to { transform: rotate(360deg); } }
.disc { position: relative; z-index: 2; display: grid; place-items: center; width: 96px; height: 96px; border-radius: 50%; background: #fff; color: var(--accent); border: 3px solid #fff; box-shadow: 0 10px 28px rgba(214, 41, 118, .18); }
.disc svg { position: relative; z-index: 1; }
.done .disc { color: #1f9d55; background: var(--t-green); animation: cheer .6s ease; }
.done .pulse, .done .orbit { display: none; }
@keyframes cheer { 30% { transform: scale(1.2) rotate(-8deg); } 60% { transform: scale(.95) rotate(4deg); } }
.fail .disc { color: var(--i-red); background: var(--t-red); animation: none; }
.fail .pulse, .fail .orbit { display: none; }
.swap-enter-active, .swap-leave-active { transition: opacity .25s, transform .25s; }
.swap-enter-from { opacity: 0; transform: scale(.5) rotate(-15deg); }
.swap-leave-to { opacity: 0; transform: scale(.6) rotate(15deg); }
.fade-enter-active, .fade-leave-active { transition: opacity .25s, transform .25s; }
.fade-enter-from { opacity: 0; transform: translateY(6px); }
.fade-leave-to { opacity: 0; transform: translateY(-6px); }
h1 { margin: 0 0 6px; font-size: clamp(22px, 3vw, 28px); font-weight: 800; letter-spacing: -.03em; }
.msg { margin: 0 0 26px; font-size: 15px; color: var(--muted); min-height: 1.5em; }
.fail .msg { color: var(--i-red); }
/* 단계 표시 */
.steps { position: relative; display: grid; grid-template-columns: repeat(5, 1fr); margin: 0 auto 22px; padding: 0; list-style: none; max-width: 520px; }
.bar { position: absolute; left: 10%; right: 10%; top: 19px; height: 4px; border-radius: 2px; background: var(--line); }
.fill { height: 100%; border-radius: 2px; background: var(--cta); transition: width .6s ease; }
.steps li { position: relative; display: grid; justify-items: center; gap: 6px; }
.node { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 50%; background: #fff; border: 2px solid var(--line-strong); color: var(--faint); transition: all .3s; }
.steps small { font-size: 12.5px; color: var(--faint); font-weight: 600; }
.steps li.on .node { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); animation: glow 1.4s ease-in-out infinite; }
.steps li.on small { color: var(--ink); }
.steps li.done .node { border-color: transparent; background: var(--cta); color: #fff; animation: pop .4s ease; }
.steps li.done small { color: var(--accent-deep); }
@keyframes glow { 0%, 100% { box-shadow: 0 0 0 0 rgba(214, 41, 118, .35); } 50% { box-shadow: 0 0 0 9px rgba(214, 41, 118, 0); } }
@keyframes pop { 40% { transform: scale(1.25); } }
/* 팁·시간·실패 */
.tip { display: inline-flex; align-items: center; gap: 6px; margin: 0; padding: 7px 14px; border-radius: 999px; background: var(--t-yellow); color: #6f5316; font-size: 13px; }
.eta { display: flex; align-items: center; justify-content: center; gap: 5px; margin: 12px 0 0; font-size: 12.5px; color: var(--faint); }
.fail-box { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 10px; }
.fail-box button { display: inline-flex; align-items: center; gap: 6px; }
.lnk { padding: 8px 12px; border-radius: 10px; font-size: 14px; font-weight: 600; color: var(--muted); text-decoration: none; }
.lnk:hover { background: var(--hover); color: var(--ink); }
@media (max-width: 640px) { .stage { padding: 32px 16px 24px; border-radius: 20px; } .steps small { font-size: 11px; } .node { width: 36px; height: 36px; } .bar { top: 16px; } }
</style>
