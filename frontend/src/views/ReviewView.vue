<template>
  <section v-if="result && form" class="review">
    <RouterLink to="/home" class="back">‹ 홈으로</RouterLink>

    <!-- 제목 -->
    <div class="head">
      <div class="chips">
        <span class="tag" :class="`tone-${CATEGORY[ex.category]?.tone ?? 'gray'}`">AI 분류 · {{ CATEGORY_LABEL[ex.category] ?? '기타' }}</span>
        <span class="tag" :class="`tone-${GRADE[grade].tone}`">{{ GRADE[grade].label }}</span>
        <span v-if="ex.demo" class="tag demo">예시 데이터</span>
      </div>
      <input v-model="form.title" class="title-input" aria-label="제목" />
      <p class="lead">내용을 확인하고 <b>확인하고 일정에 추가</b>를 누르면 캘린더에 들어가요.</p>
    </div>

    <p v-if="ex.notice" class="notice">
      <span>ⓘ</span>{{ ex.notice }}
      <RouterLink :to="{ path: '/upload', query: { url: result.original_url } }">스크린샷을 함께 올려 다시 분석하기 →</RouterLink>
    </p>

    <!-- SNS 요약 vs 공식 요약 -->
    <div class="pair">
      <div class="card">
        <h2 class="panel-title">이 링크가 알려주는 내용</h2>
        <div class="sns">
          <img v-if="ex.image_url && imgOk" :src="ex.image_url" alt="" referrerpolicy="no-referrer" @error="imgOk = false" />
          <div>
            <p>{{ ex.summary || '요약할 수 있는 내용이 없어요.' }}</p>
            <a v-if="result.original_url" :href="result.original_url" target="_blank" rel="noopener" class="link">원본 게시물 열기 ↗</a>
          </div>
        </div>
      </div>
      <div class="card official-card" :class="{ none: !primary }">
        <h2 class="panel-title">공식 공고에서는</h2>
        <template v-if="primary">
          <p>{{ ver.official_summary }}</p>
          <a :href="primary.url" target="_blank" rel="noopener" class="src">
            <b>{{ primary.title || primary.url }}</b>
            <small>{{ DOMAIN[primary.domain_type] ?? '출처' }} · {{ host(primary.url) }} ↗</small>
          </a>
        </template>
        <p v-else class="muted">같은 내용을 다루는 공식 공고를 찾지 못했어요. SNS 내용 기준으로 저장되니, 중요한 조건은 직접 한 번 더 확인해 주세요.</p>
      </div>
    </div>

    <!-- 항목별 비교 -->
    <div class="card">
      <h2 class="panel-title">항목별 확인 <small>{{ rows.length }}개 항목</small></h2>
      <CompareRows v-if="rows.length" :rows="rows" />
      <p v-else class="empty">비교할 항목을 찾지 못했어요.</p>
    </div>

    <div v-if="ex.key_points?.length" class="card">
      <h2 class="panel-title">그 밖의 정보 요약</h2>
      <ul class="points"><li v-for="p in ex.key_points" :key="p">{{ p }}</li></ul>
    </div>

    <!-- 저장할 카테고리 (홈의 9개 블록) -->
    <div class="card">
      <h2 class="panel-title">저장할 카테고리</h2>
      <div class="cats" role="radiogroup" aria-label="저장할 카테고리">
        <button v-for="c in CATEGORIES" :key="c.key" type="button" role="radio" :aria-checked="category === c.key"
                class="cat" :class="{ on: category === c.key }" @click="category = c.key">
          <CategoryArt :kind="c.key" fill /><span>{{ c.label }}</span>
        </button>
      </div>
    </div>

    <!-- 캘린더에 넣을 일정 -->
    <div class="card">
      <h2 class="panel-title">캘린더에 넣을 일정 <small v-if="multi">{{ picked.length }} / {{ form.events.length }}건 선택</small></h2>
      <template v-if="multi">
        <label v-for="(e, i) in form.events" :key="i" class="ev-row" :class="{ off: !e.on }">
          <input v-model="e.on" type="checkbox" />
          <div class="ev-main">
            <input v-model="e.title" class="ev-title" />
            <small v-if="e.location?.name">📍 {{ e.location.name }}</small>
          </div>
          <div class="dates">
            <input v-model="e.start" type="date" aria-label="시작일" @change="e.touched = true" />
            <span>~</span>
            <input v-model="e.end" type="date" aria-label="종료일" @change="e.touched = true" />
          </div>
          <b v-if="e.ambiguous && !e.touched" class="warn-dot" title="날짜가 확실하지 않아요">날짜 확인</b>
        </label>
      </template>
      <template v-else>
        <div class="date-form">
          <span class="date-label">{{ dateKind === 'event_period' ? '행사 기간' : '신청 기간 · 마감' }}</span>
          <div class="dates">
            <input v-model="form.start" type="date" aria-label="시작일" @change="form.touched = true" />
            <span>~</span>
            <input v-model="form.end" type="date" aria-label="마감일" @change="form.touched = true" />
          </div>
          <small class="muted">{{ dateSourceNote }}</small>
        </div>
        <p v-if="!form.start && !form.end" class="muted">날짜가 없으면 캘린더 대신 '저장됨'에만 들어가요. 알고 있는 날짜가 있으면 입력해 주세요.</p>
      </template>
      <p v-if="expired" class="expired">⚠ 이미 {{ expired }} 마감(종료)된 일정이에요. 그래도 기록용으로 저장할 수 있어요.</p>
      <label v-if="needsDateCheck" class="confirm-date">
        <input v-model="dateChecked" type="checkbox" />
        날짜가 확실하지 않아요(연도·말일 추정). 날짜를 확인했어요.
      </label>
    </div>

    <div class="actions">
      <p v-if="error" class="err">{{ error.message }}</p>
      <RouterLink to="/home" class="cancel">취소</RouterLink>
      <button :disabled="saving || !canSave" @click="save">{{ saving ? '저장 중…' : `확인하고 일정에 추가${multi ? ` (${picked.length}건)` : ''}` }}</button>
    </div>
  </section>
  <p v-else-if="loadError" class="empty">{{ loadError }}</p>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getShareResult, confirmShareItems } from '../api/nexto'
import { CATEGORIES, CATEGORY, CATEGORY_LABEL, GRADE, compareRows } from '../utils/labels'
import CompareRows from '../components/CompareRows.vue'
import CategoryArt from '../components/CategoryArt.vue'

const DOMAIN = { OFFICIAL_GOV: '정부·지자체 공식', OFFICIAL_PUBLIC: '공공기관 공식', OFFICIAL_FINANCE: '금융기관 공식', OFFICIAL_ORGANIZER: '주최측 공식', SECONDARY: '2차 자료', UNKNOWN: '출처' }
const LAST_ITEMS = 'nexto_last_items'
const route = useRoute(), router = useRouter()
const category = ref('OTHER'), result = ref(null), form = ref(null), saving = ref(false), error = ref(null), loadError = ref(''), imgOk = ref(true), dateChecked = ref(false)

const ex = computed(() => result.value.extraction)
const ver = computed(() => result.value.verification ?? { fields: [] })
const official = computed(() => ver.value.official ?? {})
const grade = computed(() => ver.value.overall_grade ?? 'UNVERIFIED')
const primary = computed(() => result.value.sources.find(s => s.url === ver.value.primary_source_url) ?? null)
const rows = computed(() => compareRows(ex.value, ver.value.fields))
const multi = computed(() => form.value.events.length > 0)
const picked = computed(() => form.value.events.filter(e => e.on))
const dateKind = computed(() => ex.value.category === 'EVENT' || (ex.value.event_period?.start && !ex.value.apply_period?.end) ? 'event_period' : 'apply_period')
const host = u => { try { return new URL(u).hostname.replace(/^www\./, '') } catch { return u } }

// 날짜 기본값: 공식 공고 값이 있으면 공식 기준, 없으면 SNS 기준
const officialPeriod = computed(() => official.value[dateKind.value]?.end || official.value[dateKind.value]?.start ? official.value[dateKind.value] : null)
const dateSourceNote = computed(() => form.value.touched ? '직접 입력한 날짜로 저장돼요.' : officialPeriod.value ? '공식 공고 기준 날짜로 채웠어요.' : 'SNS 내용 기준 날짜예요.')
const needsDateCheck = computed(() => multi.value
  ? picked.value.some(e => e.ambiguous && !e.touched)
  : form.value.ambiguous && !form.value.touched && (form.value.start || form.value.end))
// 마감일(없으면 시작일)이 오늘보다 이전이면 경고
const expired = computed(() => {
  const ends = multi.value ? picked.value.map(e => e.end || e.start) : [form.value.end || form.value.start]
  const today = new Date().toISOString().slice(0, 10), past = ends.filter(d => d && d < today).sort()
  if (!past.length || past.length < ends.filter(Boolean).length) return null
  const [, m, d] = past.at(-1).split('-'); return `${+m}월 ${+d}일에`
})
const canSave = computed(() => (multi.value ? picked.value.length > 0 : true) && (!needsDateCheck.value || dateChecked.value))

onMounted(async () => {
  try { result.value = await getShareResult(route.params.shareId) } catch (e) { loadError.value = e.message; return }
  const x = result.value.extraction
  category.value = CATEGORY[route.query.category] ? route.query.category : CATEGORY[x.category] ? x.category : 'OTHER'
  const period = officialPeriod.value ?? x[dateKind.value] ?? {}
  form.value = {
    title: official.value.title && ver.value.fields?.some(f => f.field === 'title' && ['VERIFIED', 'REFINED'].includes(f.status)) ? official.value.title : x.title,
    start: period.start ?? '', end: period.end ?? '', ambiguous: period.status === 'ambiguous', touched: false,
    events: (x.events ?? []).map(e => ({ on: true, title: e.title, start: e.event_period?.start ?? '', end: e.event_period?.end ?? e.event_period?.start ?? '',
                                         location: e.location, ambiguous: e.event_period?.status === 'ambiguous', touched: false }))
  }
})

// 공식 값 우선으로 저장할 필드 구성
const pick = (key) => {
  const o = official.value[key], s = ex.value[key]
  return (Array.isArray(o) ? o.length : o) ? o : s
}
function buildItems() {
  const x = ex.value, common = { summary: x.summary, official_summary: ver.value.official_summary ?? null, key_points: x.key_points, image_url: x.image_url, organization: x.organization }
  if (multi.value) {
    return picked.value.map(e => ({
      title: e.title, category: category.value, user_overrides: e.touched || dateChecked.value ? ['event_period'] : [],
      fields: { ...common, event_period: { start: e.start || null, end: e.end || e.start || null, status: 'exact' }, location: e.location }
    }))
  }
  const f = form.value
  return [{
    title: f.title, category: category.value, user_overrides: f.touched || dateChecked.value ? [dateKind.value] : [],
    fields: { ...common, target: pick('target'), eligibility: pick('eligibility'), benefit_amount: pick('benefit_amount'), requirements: pick('requirements'),
              location: pick('location'), [dateKind.value]: f.start || f.end ? { start: f.start || null, end: f.end || null, status: 'exact' } : null }
  }]
}

async function save() {
  saving.value = true; error.value = null
  try {
    const saved = await confirmShareItems(route.params.shareId, buildItems())
    try { localStorage.setItem(LAST_ITEMS, JSON.stringify(saved.map(i => i.item_id))) } catch { /* 저장 불가 환경 무시 */ }
    const first = saved.map(i => i.fields.event_period?.start ?? i.fields.apply_period?.start ?? i.fields.apply_period?.end).filter(Boolean).sort()[0]
    router.push({ path: '/home', query: { added: saved.length, ...(first ? { month: first.slice(0, 7) } : {}) } })
  } catch (e) { error.value = e } finally { saving.value = false }
}
</script>

<style scoped>
.review { display: grid; gap: 14px; padding: 16px 0 90px; }
.review > .card { margin: 0; }
.back { color: var(--faint); text-decoration: none; font-size: 14px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.tag.demo { background: #fff; color: var(--muted); border: 1px dashed var(--line); }
.title-input { margin: 10px 0 6px; padding: 2px 0; border: 0; border-radius: 0; background: none; font-family: var(--serif); font-size: clamp(24px, 3.2vw, 34px); font-weight: 700; }
.title-input:hover { background: var(--soft); }
.title-input:focus { outline: none; background: var(--soft); }
.lead { margin: 0; color: var(--muted); }
.notice { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; margin: 0; padding: 12px 16px; border-radius: 6px; background: var(--t-yellow); color: #6f5316; font-size: 14px; }
.notice span { font-weight: 700; }
.notice a { color: #9a6a12; font-weight: 600; margin-left: auto; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.pair .card { margin: 0; }
.pair p { margin: 0 0 12px; line-height: 1.7; }
.sns { display: flex; gap: 16px; align-items: flex-start; }
.sns img { flex: none; width: 104px; height: 104px; object-fit: cover; border-radius: 6px; }
.link { color: var(--blue); font-size: 14px; }
.official-card { background: var(--soft); border-color: transparent; }
.src { display: block; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px; background: #fff; text-decoration: none; }
.src:hover { background: var(--hover); }
.src b { display: block; font-size: 14px; margin-bottom: 2px; }
.src small { color: var(--muted); }
.muted { color: var(--muted); font-size: 14px; line-height: 1.6; }
.points { margin: 0; padding-left: 20px; line-height: 1.9; }
.cats { display: grid; grid-template-columns: repeat(9, 1fr); gap: 8px; }
.cat { display: grid; padding: 0; overflow: hidden; background: #fff; color: var(--ink); border: 1px solid var(--line); border-radius: 6px; font-weight: 400; text-align: center; }
.cat :deep(svg) { width: 100%; aspect-ratio: 5 / 3; display: block; }
.cat span { padding: 5px 2px; font-family: var(--serif); font-size: 12.5px; white-space: nowrap; }
.cat:hover { background: var(--soft); }
.cat.on { border-color: var(--blue); box-shadow: 0 0 0 1px var(--blue); }
.cat.on span { color: var(--blue); font-weight: 700; }
.ev-row { display: grid; grid-template-columns: auto 1fr auto auto; gap: 14px; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--line); cursor: pointer; }
.ev-row:last-of-type { border-bottom: 0; }
.ev-row.off { opacity: .45; }
.ev-row input[type=checkbox], .confirm-date input { width: 18px; height: 18px; accent-color: var(--blue); }
.ev-main small { color: var(--muted); }
.ev-title { padding: 2px 0; border: 0; background: none; font-family: var(--serif); font-weight: 700; font-size: 15px; cursor: text; }
.dates { display: flex; align-items: center; gap: 8px; }
.dates input { width: 150px; padding: 6px 8px; }
.warn-dot { font-size: 12px; font-weight: 500; color: #9a520e; background: var(--t-orange); padding: 2px 8px; border-radius: 4px; }
.date-form { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; }
.date-label { font-family: var(--serif); font-weight: 700; }
.expired { margin: 14px 0 0; padding: 10px 14px; border-radius: 6px; background: var(--t-red); color: #a8322d; font-size: 14px; }
.confirm-date { display: flex; align-items: center; gap: 10px; margin-top: 14px; padding: 10px 14px; border-radius: 6px; background: var(--t-yellow); color: #6f5316; font-size: 14px; cursor: pointer; }
.actions { position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; justify-content: flex-end; align-items: center; gap: 12px;
  padding: 12px max(48px, calc((100vw - 1040px) / 2 + 48px)); padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px)); background: rgba(255, 255, 255, .96); backdrop-filter: blur(6px); border-top: 1px solid var(--line); }
.actions button { height: 40px; padding: 0 20px; }
.cancel { color: var(--muted); text-decoration: none; padding: 0 8px; }
.err { margin: 0 auto 0 0; color: var(--i-red); font-size: 14px; }
@media (max-width: 900px) { .cats { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 760px) {
  .pair { grid-template-columns: 1fr; }
  .ev-row { grid-template-columns: auto 1fr; }
  .ev-row .dates, .ev-row .warn-dot { grid-column: 2; }
  .dates input { width: 100%; min-width: 0; }
  .actions { padding-inline: 16px; }
  .actions button { flex: 1; }
}
</style>
