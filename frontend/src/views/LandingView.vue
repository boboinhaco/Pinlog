<template>
  <div class="lp">
    <!-- 상단 바 -->
    <header class="nav" :class="{ solid: scrolled }">
      <RouterLink to="/" class="brand"><PinLogo :size="30" /></RouterLink>
      <nav class="menu">
        <a href="#problem" @click.prevent="go('problem')">이런 적 있나요</a>
        <a href="#solution" @click.prevent="go('solution')">해결 방법</a>
        <a href="#trust" @click.prevent="go('trust')">믿을 수 있나요</a>
        <a href="#faq" @click.prevent="go('faq')">자주 묻는 질문</a>
      </nav>
      <div class="nav-cta">
        <RouterLink v-if="auth.loggedIn" to="/home" class="btn-primary sm">내 페이지로</RouterLink>
        <template v-else>
          <button class="ghost sm" @click="go('login')">로그인</button>
          <button class="primary sm" @click="go('login')">무료로 시작하기</button>
        </template>
      </div>
    </header>

    <!-- 1. Hero -->
    <section class="hero">
      <span class="blob b1" aria-hidden="true"></span><span class="blob b2" aria-hidden="true"></span>
      <div class="hero-in">
        <div class="hero-text">
          <p v-reveal class="eyebrow"><Sparkles :size="15" />SNS 링크 → 확인된 일정</p>
          <h1 v-reveal="60">저장만 해둔 그 링크,<br><span class="grad-text">다음 일정</span>으로 만들어드려요.</h1>
          <p v-reveal="140" class="lead">{{ BRAND_KO }}는 인스타그램·블로그·기사 링크에서 일정과 장소를 뽑아내고,
            <b>공식 공고와 한 줄씩 대조한 뒤</b> 내가 확인한 것만 캘린더와 지도에 정리해요.</p>
          <div v-reveal="220" class="hero-cta">
            <button class="primary lg" @click="go('login')"><Sparkles :size="18" />무료로 시작하기<ArrowRight :size="18" /></button>
            <button class="ghost lg" :disabled="busy" @click="tryDemo">{{ busy ? '준비 중…' : '로그인 없이 둘러보기' }}</button>
          </div>
          <ul v-reveal="300" class="hero-points">
            <li><Check :size="15" />가입 없이 데모 체험</li><li><Check :size="15" />공식 출처 근거 표시</li><li><Check :size="15" />확인 후에만 저장</li>
          </ul>
        </div>

        <!-- 데모 목업: 링크 → 추출 결과 -->
        <div v-reveal="160" class="mock">
          <div class="mock-bar"><span class="ic"><Link2 :size="16" /></span><span class="url">instagram.com/p/…</span><span class="go-btn"><Sparkles :size="12" />일정 추출</span></div>
          <div class="mock-body">
            <div class="mock-row" v-for="(m, i) in MOCK" :key="m.title" :style="{ animationDelay: `${0.5 + i * 0.45}s` }">
              <span class="dot" :class="`tone-${m.tone}`"></span>
              <span class="mr-txt"><b>{{ m.title }}</b><small>{{ m.date }} · {{ m.place }}</small></span>
              <span class="tag" :class="`tone-${m.tone}`">{{ m.tag }}</span>
            </div>
            <div class="mock-foot"><ShieldCheck :size="15" />공식 공고와 4개 항목 대조 완료</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. 문제 제기 -->
    <section id="problem" class="sec problem">
      <p v-reveal class="kicker">이런 적 있지 않나요?</p>
      <h2 v-reveal="60">좋은 정보를 저장은 했는데,<br>정작 <span class="u">신청은 놓쳤어요.</span></h2>
      <div class="cards3">
        <article v-for="(p, i) in PROBLEMS" :key="p.title" v-reveal="120 + i * 90" class="pcard">
          <span class="picon"><component :is="p.icon" :size="24" /></span>
          <h3>{{ p.title }}</h3>
          <p>{{ p.body }}</p>
        </article>
      </div>
    </section>

    <!-- 3. 해결책 -->
    <section id="solution" class="sec">
      <p v-reveal class="kicker">{{ BRAND_KO }}가 하는 일</p>
      <h2 v-reveal="60">링크 하나면 충분해요</h2>
      <div class="values">
        <article v-for="(v, i) in VALUES" :key="v.title" v-reveal="100 + i * 80" class="vcard">
          <div class="vfig" :class="v.key">
            <!-- 각 가치의 미니 시각화 -->
            <template v-if="v.key === 'extract'">
              <span class="chipline"><i class="tag tone-pink">일정</i><i class="tag tone-blue">장소</i><i class="tag tone-yellow">대상</i><i class="tag tone-green">마감</i></span>
              <span class="arrowdown"><ArrowRight :size="18" /></span>
              <span class="mini-card"><CalendarDays :size="16" /><b>서울 재즈 페스티벌</b><small>9.12 – 9.14 · 올림픽공원</small></span>
            </template>
            <template v-else-if="v.key === 'verify'">
              <span class="cmp-row"><small>대상</small><b>19~34세</b><i class="tag tone-red">내용이 달라요</i></span>
              <span class="cmp-row"><small>신청 기간</small><b>9.1 – 9.30</b><i class="tag tone-green">일치</i></span>
              <span class="cmp-row"><small>자격요건</small><b>소득 기준</b><i class="tag tone-purple">공식에만 있음</i></span>
            </template>
            <template v-else>
              <span class="cal-mini">
                <i v-for="n in 21" :key="n" :class="{ on: [5, 6, 7, 12, 18, 19].includes(n) }"></i>
              </span>
              <span class="pin-mini"><MapPin :size="14" />올림픽공원 · 성수 · 예술의전당</span>
            </template>
          </div>
          <h3>{{ v.title }}</h3>
          <p>{{ v.body }}</p>
        </article>
      </div>
    </section>

    <!-- 4. 신뢰 요소 -->
    <section id="trust" class="sec trust">
      <p v-reveal class="kicker">믿을 수 있나요?</p>
      <h2 v-reveal="60">AI가 지어내지 않도록,<br>근거를 함께 보여줘요</h2>
      <div class="trust-grid">
        <article v-reveal="100" class="tcard wide">
          <h3><ShieldCheck :size="18" />공식 출처와 한 줄씩 대조</h3>
          <div class="evi">
            <div class="evi-row"><small>SNS 링크</small><b>서울 거주 19~34세 청년</b></div>
            <div class="evi-row off"><small>공식 공고</small><b>만 19~39세 무주택 청년</b><i class="tag tone-red">내용이 달라요</i></div>
            <blockquote>“지원대상: 만 19세 이상 39세 이하 서울시 거주 무주택 청년” <cite>youth.seoul.go.kr</cite></blockquote>
          </div>
        </article>
        <article v-reveal="180" class="tcard">
          <h3><BadgeCheck :size="18" />3단계 신뢰 표시</h3>
          <ul class="grades">
            <li><i class="tag tone-green">공식 근거 확인</i><span>공식 공고에서 핵심 항목이 확인된 경우</span></li>
            <li><i class="tag tone-orange">확인 필요</i><span>공식 정보와 다르거나 애매한 항목이 있는 경우</span></li>
            <li><i class="tag tone-gray">공식 미확인</i><span>같은 내용을 다루는 공식 출처를 못 찾은 경우</span></li>
          </ul>
        </article>
        <article v-reveal="240" class="tcard">
          <h3><Globe :size="18" />이런 곳을 먼저 찾아요</h3>
          <div class="domains"><span v-for="d in DOMAINS" :key="d">{{ d }}</span></div>
          <p class="note">비슷해 보인다고 아무 출처나 연결하지 않아요. 찾지 못하면 <b>‘공식 미확인’</b>으로 정직하게 표시해요.</p>
        </article>
        <article v-reveal="300" class="tcard">
          <h3><CalendarCheck :size="18" />저장은 내가 확인한 뒤에</h3>
          <p class="note">날짜가 추정값이면 확인 체크를 해야 저장돼요. 이미 마감된 일정은 경고로 알려드려요.</p>
          <span class="check-demo"><Check :size="14" />날짜를 확인했어요</span>
        </article>
      </div>
    </section>

    <!-- 5. 프로세스 -->
    <section id="process" class="sec">
      <p v-reveal class="kicker">어떻게 쓰나요</p>
      <h2 v-reveal="60">4단계면 끝나요</h2>
      <ol class="steps">
        <li v-for="(s, i) in STEPS" :key="s.title" v-reveal="80 + i * 90">
          <span class="num">{{ i + 1 }}</span>
          <span class="sicon"><component :is="s.icon" :size="22" /></span>
          <h3>{{ s.title }}</h3>
          <p>{{ s.body }}</p>
        </li>
      </ol>
    </section>

    <!-- 6. FAQ -->
    <section id="faq" class="sec faq">
      <p v-reveal class="kicker">자주 묻는 질문</p>
      <h2 v-reveal="60">궁금한 점을 모았어요</h2>
      <div class="faq-list">
        <details v-for="(f, i) in FAQ" :key="f.q" v-reveal="60 + i * 60" :open="i === 0">
          <summary>{{ f.q }}<ChevronDown :size="18" /></summary>
          <p>{{ f.a }}</p>
        </details>
      </div>
    </section>

    <!-- 7. 최종 CTA + 로그인 -->
    <section id="login" class="sec cta">
      <div class="cta-in">
        <div v-reveal class="cta-copy">
          <p class="kicker light">지금 시작하기</p>
          <h2>좋아하는 콘텐츠가<br>특별한 일정이 되는 순간</h2>
          <p class="lead">가입하면 내 일정과 장소가 계정에 저장돼요.<br>먼저 둘러보고 싶다면 데모로 체험해보세요.</p>
          <ul class="hero-points light">
            <li><Check :size="15" />이메일만으로 가입</li><li><Check :size="15" />언제든 삭제 가능</li>
          </ul>
        </div>
        <div v-reveal="120" class="login-card">
          <template v-if="auth.loggedIn">
            <h3>이미 로그인되어 있어요</h3>
            <p class="note">{{ auth.displayName || '데모 계정' }}으로 이용 중이에요.</p>
            <RouterLink to="/home" class="btn-primary full">내 페이지로 가기</RouterLink>
          </template>
          <template v-else>
            <h3>{{ mode === 'signup' ? '회원가입' : '로그인' }}</h3>
            <p v-if="route.query.expired" class="note warn">세션이 끝났어요. 다시 로그인해 주세요.</p>
            <p v-else class="note">이메일과 비밀번호만 있으면 돼요.</p>
            <AuthForm :initial-mode="route.query.next ? 'login' : 'signup'" @mode="m => (mode = m)" @done="goNext" />
            <div class="or"><span>또는</span></div>
            <button class="ghost full" :disabled="busy" @click="tryDemo">{{ busy ? '준비 중…' : '로그인 없이 둘러보기 (데모)' }}</button>
          </template>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Sparkles, ArrowRight, Check, Link2, ShieldCheck, BadgeCheck, Globe, CalendarCheck, CalendarDays, MapPin,
         ChevronDown, BookmarkX, SearchX, CalendarX, Wand2, ListChecks, MapPinned } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { BRAND_KO } from '../utils/brand'
import { vReveal as reveal } from '../utils/reveal'
import PinLogo from '../components/PinLogo.vue'
import AuthForm from '../components/AuthForm.vue'
import AppFooter from '../components/AppFooter.vue'

const vReveal = reveal
const MOCK = [
  { title: '서울 재즈 페스티벌', date: '9.12 – 9.14', place: '올림픽공원', tag: '축제·행사', tone: 'pink' },
  { title: '청년 월세 지원 신청', date: '9.1 – 9.30', place: '온라인 신청', tag: '청년 주거', tone: 'green' },
  { title: '청년 적금 가입 마감', date: '10.16', place: '은행 앱', tag: '금융상품', tone: 'yellow' }
]
const PROBLEMS = [
  { icon: BookmarkX, title: '저장만 하고 잊어버려요', body: '“나중에 신청해야지” 하고 저장한 게시물이 피드 아래로 사라져요. 마감일은 지나 있고요.' },
  { icon: SearchX, title: '진짜인지 확인이 어려워요', body: '나이 조건, 소득 기준, 마감일이 게시물마다 다르게 적혀 있어요. 공식 공고는 어디에 있는지도 모르겠고요.' },
  { icon: CalendarX, title: '날짜와 장소가 흩어져요', body: '캘린더에 옮겨 적고, 지도를 따로 검색하고… 정리하다 지쳐서 결국 안 가게 돼요.' }
]
const VALUES = [
  { key: 'extract', title: '링크에서 핵심만 뽑아요', body: '캡션과 이미지를 읽어 이름·대상·자격요건·기간·장소를 구조화해요. 게시물 하나에 일정이 여러 개여도 각각 나눠줘요.' },
  { key: 'verify', title: '공식 공고와 대조해요', body: '정부·지자체·은행 같은 공식 출처를 찾아 항목별로 비교하고, 근거 문장을 그대로 함께 보여줘요.' },
  { key: 'organize', title: '캘린더와 지도로 정리해요', body: '확인한 일정만 저장되고, 장소는 자동으로 지도에 찍혀요. 카테고리별로 모아보고 마감 알림도 받아요.' }
]
const DOMAINS = ['정부·지자체 (go.kr)', '공공기관', '금융기관', '주최측 공식 페이지']
const STEPS = [
  { icon: Link2, title: '링크 붙여넣기', body: '인스타그램·블로그·기사 링크를 그대로 붙여넣어요.' },
  { icon: Wand2, title: 'AI가 정보 추출', body: '캡션과 이미지에서 일정·장소·조건을 찾아내요.' },
  { icon: ListChecks, title: '공식 공고와 비교 확인', body: '항목별 대조 결과를 보고 날짜와 내용을 확인해요.' },
  { icon: MapPinned, title: '캘린더·지도에 저장', body: '확인한 것만 저장돼요. 카테고리로 모아볼 수 있어요.' }
]
const FAQ = [
  { q: '어떤 링크를 넣을 수 있나요?', a: '인스타그램 게시물, 네이버 블로그, 뉴스 기사처럼 공개된 웹 링크면 됩니다. 인스타그램은 캡션과 첫 이미지를 읽어요. 여러 장 슬라이드의 뒷장은 읽을 수 없어서, 그럴 때는 스크린샷을 함께 올리면 돼요.' },
  { q: '공식 공고는 어떻게 찾나요?', a: '추출한 사업·상품·행사 이름으로 웹을 검색한 뒤, 정부·지자체·공공기관·금융기관처럼 공식 도메인을 먼저 봅니다. 같은 대상을 다루는 공식 문서를 찾지 못하면 연결하지 않고 ‘공식 미확인’으로 표시해요.' },
  { q: 'AI가 잘못 읽으면 어떻게 하나요?', a: '분석 결과는 바로 저장되지 않아요. 확인 화면에서 제목·날짜·카테고리를 직접 고칠 수 있고, 추정한 날짜는 확인 체크를 해야 저장됩니다.' },
  { q: '가입하지 않아도 쓸 수 있나요?', a: '데모 계정으로 둘러볼 수 있어요. 다만 데모는 모두가 함께 쓰는 계정이라, 내 일정만 따로 모으려면 가입이 필요해요.' },
  { q: '어떤 정보를 저장하나요?', a: '이메일, 비밀번호(암호화), 그리고 직접 저장한 일정·장소·메모만 저장해요. 프로필 사진은 올린 경우에만 저장됩니다.' },
  { q: '비용이 드나요?', a: '현재는 무료로 쓸 수 있어요. 원티드 AI 챔피언십 출품작으로 개발 중인 서비스입니다.' }
]

const auth = useAuthStore(), router = useRouter(), route = useRoute()
const busy = ref(false), mode = ref('signup'), scrolled = ref(false)
// 로그인 후에는 원래 가려던 페이지로 (앱 내부 경로만 허용)
const next = typeof route.query.next === 'string' && route.query.next.startsWith('/') && !route.query.next.startsWith('//') ? route.query.next : '/home'
const goNext = () => router.push(next)
const go = id => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: id === 'login' ? 'center' : 'start' })
async function tryDemo() {
  busy.value = true
  try { await auth.demo(); goNext() } finally { busy.value = false }
}
const onScroll = () => (scrolled.value = window.scrollY > 20)
onMounted(() => {
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true })
  // 보호된 페이지에서 넘어왔거나 /login 으로 들어오면 로그인 영역으로
  if (route.query.next || route.query.expired || route.hash === '#login') setTimeout(() => go('login'), 350)
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.lp { background: var(--bg); overflow-x: clip; }
/* 상단 바 */
.nav { position: sticky; top: 0; z-index: 100; display: flex; align-items: center; gap: 28px; height: 68px; padding: 0 32px; transition: background .25s, box-shadow .25s, border-color .25s; border-bottom: 1px solid transparent; }
.nav.solid { background: rgba(255, 255, 255, .85); backdrop-filter: saturate(180%) blur(16px); border-bottom-color: var(--line); }
.brand { text-decoration: none; }
.menu { display: flex; gap: 6px; margin-left: 12px; }
.menu a { padding: 8px 12px; border-radius: 10px; color: var(--muted); font-weight: 600; font-size: 14.5px; text-decoration: none; }
.menu a:hover { color: var(--ink); background: var(--hover); }
.nav-cta { margin-left: auto; display: flex; gap: 8px; }
.sm { padding: 8px 16px; font-size: 14px; border-radius: 12px; }
.btn-primary { display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: var(--cta); color: #fff; border-radius: 12px; text-decoration: none; font-weight: 600; box-shadow: 0 6px 18px rgba(221, 42, 123, .25); }
.lg { height: 54px; padding: 0 26px; font-size: 16px; border-radius: 16px; display: inline-flex; align-items: center; gap: 8px; }

/* 1. Hero */
.hero { position: relative; padding: 70px 32px 96px; overflow: hidden; }
.hero-in { position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.05fr .95fr; gap: 56px; align-items: center; }
.blob { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .5; animation: float 14s ease-in-out infinite; }
.b1 { width: 460px; height: 460px; top: -140px; right: -60px; background: radial-gradient(circle at 30% 30%, #ffd9b0, #ffb3d1); }
.b2 { width: 380px; height: 380px; bottom: -160px; left: -80px; background: radial-gradient(circle at 60% 40%, #e2ccff, #ffd0e4); animation-delay: -6s; }
@keyframes float { 0%, 100% { transform: translate3d(0, 0, 0) scale(1); } 50% { transform: translate3d(0, -26px, 0) scale(1.06); } }
.eyebrow { display: inline-flex; align-items: center; gap: 6px; margin: 0 0 16px; padding: 7px 14px; border-radius: 999px; background: #fff; border: 1px solid var(--line-strong); font-size: 13.5px; font-weight: 700; color: var(--accent); }
h1 { margin: 0 0 18px; font-size: clamp(34px, 4.4vw, 56px); line-height: 1.22; letter-spacing: -.045em; }
.lead { margin: 0; font-size: 17px; line-height: 1.8; color: var(--muted); max-width: 540px; }
.lead b { color: var(--ink); }
.hero-cta { display: flex; flex-wrap: wrap; gap: 12px; margin: 28px 0 18px; }
.hero-points { display: flex; flex-wrap: wrap; gap: 8px 20px; margin: 0; padding: 0; list-style: none; font-size: 14px; color: var(--muted); }
.hero-points li { display: inline-flex; align-items: center; gap: 6px; }
.hero-points .lucide { color: var(--accent); }

/* 히어로 목업 */
.mock { background: #fff; border: 1px solid var(--line); border-radius: 24px; box-shadow: var(--shadow-lg); padding: 14px; transform: rotate(-1deg); }
.mock-bar { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 16px; background: var(--soft); border: 1px solid var(--line); }
.mock-bar .ic { display: grid; place-items: center; width: 32px; height: 32px; border-radius: 10px; background: var(--grad-soft); color: var(--accent); }
.url { flex: 1; font-size: 13.5px; color: var(--faint); }
.go-btn { display: inline-flex; align-items: center; gap: 5px; padding: 7px 12px; border-radius: 10px; background: var(--cta); color: #fff; font-size: 12.5px; font-weight: 700; }
.mock-body { padding: 14px 4px 4px; display: grid; gap: 8px; }
.mock-row { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 14px; border: 1px solid var(--line); opacity: 0; animation: rowIn .5s ease forwards; }
@keyframes rowIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.mock-row .dot { width: 10px; height: 10px; border-radius: 50%; }
.mr-txt { flex: 1; display: grid; min-width: 0; }
.mr-txt b { font-size: 14px; }
.mr-txt small { font-size: 12px; color: var(--muted); }
.mock-foot { display: flex; align-items: center; gap: 8px; margin-top: 4px; padding: 10px 12px; border-radius: 12px; background: var(--t-green); color: #1f7a48; font-size: 13px; font-weight: 600; }

/* 공통 섹션 */
.sec { max-width: 1200px; margin: 0 auto; padding: 96px 32px; text-align: center; }
.kicker { margin: 0 0 10px; font-size: 14px; font-weight: 800; letter-spacing: .02em; background: var(--cta); -webkit-background-clip: text; background-clip: text; color: transparent; }
.kicker.light { background: none; color: #ffd9ec; -webkit-text-fill-color: currentColor; }
.sec h2 { margin: 0 0 44px; font-size: clamp(26px, 3.2vw, 40px); line-height: 1.35; letter-spacing: -.04em; }
.u { background: linear-gradient(transparent 62%, #ffd9ec 62%); }

/* 2. 문제 */
.cards3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.pcard { padding: 28px 24px; background: #fff; border: 1px solid var(--line); border-radius: 22px; text-align: left; box-shadow: var(--shadow); }
.picon { display: grid; place-items: center; width: 52px; height: 52px; border-radius: 16px; background: var(--grad-soft); color: var(--accent); }
.pcard h3 { margin: 16px 0 8px; font-size: 18px; }
.pcard p { margin: 0; font-size: 14.5px; line-height: 1.75; color: var(--muted); }

/* 3. 해결책 */
.values { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.vcard { padding: 22px; background: #fff; border: 1px solid var(--line); border-radius: 22px; text-align: left; box-shadow: var(--shadow); transition: transform .25s, box-shadow .25s; }
.vcard:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.vfig { display: grid; gap: 10px; align-content: center; justify-items: center; height: 186px; padding: 18px; border-radius: 18px; background: var(--soft); }
.chipline { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.chipline i, .cmp-row i { font-style: normal; }
.arrowdown { color: var(--faint); transform: rotate(90deg); }
.mini-card { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; width: 100%; padding: 10px 12px; border-radius: 12px; background: #fff; border: 1px solid var(--line); }
.mini-card .lucide { grid-row: span 2; align-self: center; color: var(--accent); }
.mini-card b { font-size: 13.5px; }
.mini-card small { font-size: 12px; color: var(--muted); }
.cmp-row { display: flex; align-items: center; gap: 8px; width: 100%; padding: 9px 12px; border-radius: 12px; background: #fff; border: 1px solid var(--line); font-size: 13px; }
.cmp-row small { color: var(--muted); width: 62px; flex: none; }
.cmp-row b { flex: 1; font-size: 13px; }
.cal-mini { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; width: 100%; }
.cal-mini i { aspect-ratio: 1; border-radius: 5px; background: #fff; border: 1px solid var(--line); }
.cal-mini i.on { background: var(--cta); border-color: transparent; }
.pin-mini { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 999px; background: #fff; border: 1px solid var(--line); font-size: 12.5px; color: var(--muted); }
.pin-mini .lucide { color: var(--accent); }
.vcard h3 { margin: 18px 0 8px; font-size: 18px; }
.vcard p { margin: 0; font-size: 14.5px; line-height: 1.75; color: var(--muted); }

/* 4. 신뢰 */
.trust { background: linear-gradient(180deg, #fff 0%, var(--soft) 100%); max-width: none; }
.trust > * { max-width: 1200px; margin-inline: auto; }
.trust-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
.tcard { padding: 24px; background: #fff; border: 1px solid var(--line); border-radius: 22px; text-align: left; box-shadow: var(--shadow); }
.tcard.wide { grid-column: span 2; }
.tcard h3 { display: flex; align-items: center; gap: 8px; margin: 0 0 16px; font-size: 17px; }
.tcard h3 .lucide { color: var(--accent); }
.evi { display: grid; gap: 8px; }
.evi-row { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 14px; background: var(--soft); font-size: 14px; }
.evi-row.off { background: var(--t-red); }
.evi-row small { width: 74px; flex: none; color: var(--muted); }
.evi-row b { flex: 1; }
.evi-row i { font-style: normal; }
blockquote { margin: 4px 0 0; padding: 10px 14px; border-left: 3px solid var(--accent); font-size: 13px; color: var(--muted); }
cite { display: block; margin-top: 4px; font-style: normal; font-size: 12px; color: var(--faint); }
.grades { margin: 0; padding: 0; list-style: none; display: grid; gap: 12px; }
.grades li { display: flex; align-items: flex-start; gap: 10px; font-size: 13.5px; color: var(--muted); }
.grades i { font-style: normal; flex: none; }
.domains { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.domains span { padding: 7px 14px; border-radius: 999px; background: var(--soft); border: 1px solid var(--line); font-size: 13px; font-weight: 600; }
.note { margin: 0; font-size: 13.5px; line-height: 1.75; color: var(--muted); }
.check-demo { display: inline-flex; align-items: center; gap: 6px; margin-top: 14px; padding: 8px 14px; border-radius: 12px; background: var(--t-yellow); color: #8a6412; font-size: 13px; font-weight: 600; }

/* 5. 프로세스 */
.steps { position: relative; display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin: 0; padding: 0; list-style: none; }
.steps::before { content: ''; position: absolute; left: 12%; right: 12%; top: 26px; height: 2px; background: linear-gradient(90deg, #ffd9b0, #ffb3d1, #e2ccff); }
.steps li { position: relative; padding: 0 10px; text-align: center; }
.num { position: relative; z-index: 1; display: grid; place-items: center; width: 52px; height: 52px; margin: 0 auto; border-radius: 50%; background: var(--cta); color: #fff; font-size: 18px; font-weight: 800; box-shadow: 0 6px 18px rgba(221, 42, 123, .25); }
.sicon { display: grid; place-items: center; width: 44px; height: 44px; margin: 16px auto 0; border-radius: 14px; background: #fff; border: 1px solid var(--line); color: var(--accent); }
.steps h3 { margin: 12px 0 6px; font-size: 16.5px; }
.steps p { margin: 0; font-size: 14px; line-height: 1.7; color: var(--muted); }

/* 6. FAQ */
.faq-list { display: grid; gap: 10px; text-align: left; }
details { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 4px 20px; box-shadow: var(--shadow); }
summary { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 0; font-size: 16px; font-weight: 700; cursor: pointer; list-style: none; }
summary::-webkit-details-marker { display: none; }
summary .lucide { flex: none; color: var(--muted); transition: transform .25s; }
details[open] summary .lucide { transform: rotate(180deg); }
details p { margin: 0 0 20px; font-size: 14.5px; line-height: 1.85; color: var(--muted); animation: fade .3s ease; }
@keyframes fade { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }

/* 7. 최종 CTA */
.cta { max-width: none; padding-block: 0; }
.cta-in { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.05fr .95fr; gap: 48px; align-items: center; padding: 72px 32px; border-radius: 0; background: var(--cta); color: #fff; text-align: left; }
.cta-copy h2 { margin: 6px 0 16px; color: #fff; }
.cta-copy .lead { color: rgba(255, 255, 255, .88); }
.hero-points.light { margin-top: 18px; color: rgba(255, 255, 255, .9); }
.hero-points.light .lucide { color: #fff; }
.login-card { padding: 26px; background: #fff; border-radius: 24px; box-shadow: 0 20px 50px rgba(0, 0, 0, .18); color: var(--ink); }
.login-card h3 { margin: 0 0 4px; font-size: 20px; }
.login-card .note { margin: 0 0 16px; }
.login-card .warn { color: var(--i-red); font-weight: 600; }
.login-card :deep(button:not(.text)) { height: 46px; background: var(--cta); color: #fff; }
.full { width: 100%; height: 46px; display: inline-flex; align-items: center; justify-content: center; }
.or { position: relative; margin: 16px 0; text-align: center; font-size: 12px; color: var(--faint); }
.or::before { content: ''; position: absolute; left: 0; right: 0; top: 50%; border-top: 1px solid var(--line); }
.or span { position: relative; padding: 0 10px; background: #fff; }
.login-card .ghost.full { background: #fff !important; color: var(--ink); border: 1px solid var(--line-strong); }

/* 등장 애니메이션 */
:global(.reveal) { opacity: 0; transform: translateY(18px); transition: opacity .6s cubic-bezier(.2, .7, .3, 1), transform .6s cubic-bezier(.2, .7, .3, 1); }
:global(.reveal-in) { opacity: 1; transform: none; }

@media (max-width: 1000px) {
  .hero-in, .cta-in { grid-template-columns: 1fr; }
  .cards3, .values, .trust-grid, .steps { grid-template-columns: 1fr 1fr; }
  .tcard.wide { grid-column: span 2; }
  .steps::before { display: none; }
  .menu { display: none; }
}
@media (max-width: 680px) {
  .hero { padding: 40px 16px 64px; }
  .sec { padding: 64px 16px; }
  .cards3, .values, .trust-grid, .steps { grid-template-columns: 1fr; }
  .tcard.wide { grid-column: auto; }
  .nav { padding: 0 14px; gap: 10px; }
  .cta-in { padding: 56px 16px; }
  .hero-cta .lg { width: 100%; justify-content: center; }
}
</style>
