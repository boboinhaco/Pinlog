<template>
  <div class="landing">
    <header class="top">
      <RouterLink to="/" class="brand"><SproutIcon :size="20" />NEXTO</RouterLink>
      <nav>
        <template v-if="auth.loggedIn"><RouterLink to="/home" class="btn">내 페이지로</RouterLink></template>
        <template v-else>
          <RouterLink to="/login" class="link">로그인</RouterLink>
          <RouterLink to="/login?mode=signup" class="btn">무료로 시작하기</RouterLink>
        </template>
      </nav>
    </header>

    <CoverHeader title="NEXTO" subtitle="SNS에서 본 좋은 정보를, 확인된 다음 일정으로" height="340px" />

    <div class="page">
      <section class="hero">
        <h2 class="lead">링크 하나만 붙여넣으세요.<br>공식 공고와 비교해서, 캘린더에 넣어드려요.</h2>
        <p class="sub">인스타그램에서 본 청년 월세 지원, 적금 특판, 가을 축제… 저장만 해두고 잊어버렸나요?
          NEXTO는 게시물의 내용·대상·자격요건·마감일을 뽑아 공식 출처와 맞춰본 뒤, 확인한 것만 일정으로 정리해요.</p>
        <div class="cta">
          <RouterLink v-if="!auth.loggedIn" to="/login?mode=signup" class="btn big">무료로 시작하기</RouterLink>
          <RouterLink v-else to="/home" class="btn big">내 페이지로</RouterLink>
          <button class="ghost big" :disabled="busy" @click="tryDemo">{{ busy ? '준비 중…' : '로그인 없이 둘러보기' }}</button>
        </div>
      </section>

      <!-- 사용 흐름 -->
      <section class="steps">
        <div v-for="(s, i) in STEPS" :key="s.title" class="step">
          <span class="no serif">{{ i + 1 }}</span>
          <h3>{{ s.title }}</h3>
          <p>{{ s.body }}</p>
          <div class="mini" v-html="s.mini"></div>
        </div>
      </section>

      <!-- 카테고리 미리보기 -->
      <section class="block">
        <h2 class="section-title"><span>My Notebook</span><small>저장은 9개 카테고리로</small></h2>
        <div class="gallery">
          <div v-for="c in CATEGORIES" :key="c.key" class="card-cat">
            <div class="art"><CategoryArt :kind="c.key" /></div>
            <div class="label"><b class="serif">{{ c.label }}</b><small>{{ c.desc }}</small></div>
          </div>
        </div>
      </section>

      <!-- 캘린더 미리보기 -->
      <section class="block">
        <h2 class="section-title"><span>˚❀⋆.ೃ࿔*:･ Calendar ˚❀⋆.ೃ࿔*:･</span><small>확인한 일정만 캘린더와 지도에</small></h2>
        <NotionCalendar v-model:month="month" :events="sample" :linkable="false" />
      </section>

      <section class="closing callout">
        <SproutIcon :size="44" />
        <div>
          <p class="serif">Collect today, plan tomorrow.</p>
          <small>좋아하는 콘텐츠가 더 특별한 경험으로 이어지도록, NEXTO가 함께할게요.</small>
        </div>
        <RouterLink :to="auth.loggedIn ? '/home' : '/login?mode=signup'" class="btn">시작하기</RouterLink>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { CATEGORIES } from '../utils/labels'
import { ymd } from '../utils/events'
import CoverHeader from '../components/CoverHeader.vue'
import CategoryArt from '../components/CategoryArt.vue'
import NotionCalendar from '../components/NotionCalendar.vue'
import SproutIcon from '../components/SproutIcon.vue'

const STEPS = [
  { title: '링크 붙여넣기', body: '인스타그램·블로그·기사 링크를 넣으면 캡션과 이미지를 읽어 핵심 정보를 뽑아요.',
    mini: '<div class="m-input">https://instagram.com/p/…</div><div class="m-btn">가져오기</div>' },
  { title: '공식 공고와 비교', body: '대상, 자격요건, 신청 기간, 혜택을 공식 출처와 한 줄씩 대조해요.',
    mini: '<div class="m-row"><span>대상</span><i class="tag tone-red">내용이 달라요</i></div><div class="m-row"><span>신청 기간</span><i class="tag tone-green">일치</i></div><div class="m-row"><span>자격요건</span><i class="tag tone-purple">공식에만 있음</i></div>' },
  { title: '확인하면 캘린더에', body: '내가 확인한 날짜만 캘린더와 지도에 들어가고, 카테고리별로 모아둘 수 있어요.',
    mini: '<div class="m-chip tone-green">청년 월세 신청</div><div class="m-chip tone-pink">재즈 페스티벌</div><div class="m-chip tone-yellow">청년 적금 마감</div>' }
]
const auth = useAuthStore(), router = useRouter(), busy = ref(false)
const now = new Date(), month = ref(new Date(now.getFullYear(), now.getMonth(), 1))
const day = n => ymd(new Date(now.getFullYear(), now.getMonth(), n))
// 캘린더 미리보기용 예시 일정
const sample = [
  { id: 's1', title: '청년 월세 지원 신청', start: day(2), end: day(12), category: 'POLICY_HOUSING' },
  { id: 's2', title: '재즈 페스티벌', start: day(12), end: day(14), category: 'EVENT' },
  { id: 's3', title: '청년 적금 가입', start: day(15), end: day(17), category: 'FINANCE' },
  { id: 's4', title: '서포터즈 모집 마감', start: day(19), end: day(19), category: 'RECRUIT' },
  { id: 's5', title: '전시회', start: day(22), end: day(25), category: 'EVENT' },
  { id: 's6', title: '영상 공모전 접수', start: day(24), end: day(28), category: 'CONTEST' }
]

async function tryDemo() {
  busy.value = true
  try { await auth.demo(); router.push('/home') } finally { busy.value = false }
}
</script>

<style scoped>
.top { position: absolute; top: 0; left: 0; right: 0; z-index: 10; display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; }
.brand { display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; background: rgba(255, 255, 255, .85); color: var(--ink); text-decoration: none; font-family: var(--serif); font-weight: 700; }
.top nav { display: flex; align-items: center; gap: 8px; }
.link { padding: 6px 12px; border-radius: 6px; background: rgba(255, 255, 255, .85); text-decoration: none; font-size: 14px; }
.btn { display: inline-block; padding: 7px 14px; border-radius: 6px; background: var(--blue); color: #fff; text-decoration: none; font-size: 14px; font-weight: 500; }
.big { padding: 11px 20px; font-size: 15px; }
.hero { max-width: 760px; }
.lead { margin: 12px 0 14px; font-size: clamp(24px, 3.4vw, 34px); line-height: 1.4; }
.sub { margin: 0; color: var(--muted); font-size: 16px; line-height: 1.8; }
.cta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 64px; }
.step { border: 1px solid var(--line); border-radius: 8px; padding: 18px; }
.no { display: inline-grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; background: var(--mint); color: var(--mint-ink); font-size: 14px; }
.step h3 { margin: 10px 0 6px; font-size: 17px; }
.step p { margin: 0 0 14px; color: var(--muted); font-size: 14px; line-height: 1.7; }
.mini { display: grid; gap: 6px; padding: 12px; border-radius: 6px; background: var(--soft); font-size: 12.5px; }
.mini :deep(.m-input) { padding: 6px 8px; border: 1px solid var(--line); border-radius: 4px; background: #fff; color: var(--faint); }
.mini :deep(.m-btn) { justify-self: end; padding: 3px 10px; border-radius: 4px; background: var(--blue); color: #fff; }
.mini :deep(.m-row) { display: flex; justify-content: space-between; align-items: center; }
.mini :deep(i) { font-style: normal; }
.mini :deep(.m-chip) { padding: 3px 8px; border-radius: 4px; font-family: var(--serif); box-shadow: 0 1px 2px rgba(15, 15, 15, .08); }
.block { margin-top: 64px; }
.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.card-cat { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
.art { aspect-ratio: 5 / 3; border-bottom: 1px solid var(--line); }
.art :deep(svg) { width: 100%; height: 100%; display: block; }
.label { padding: 8px 10px; display: grid; }
.label b { font-size: 14px; }
.label small { color: var(--faint); font-size: 12.5px; }
.closing { align-items: center; margin-top: 64px; background: var(--mint); }
.closing div { flex: 1; }
.closing p { margin: 0; font-size: 18px; font-weight: 700; }
.closing small { color: var(--muted); }
@media (max-width: 760px) {
  .steps { grid-template-columns: 1fr; }
  .gallery { grid-template-columns: repeat(2, 1fr); }
  .closing { flex-wrap: wrap; }
  .top { padding: 10px 12px; }
}
</style>
