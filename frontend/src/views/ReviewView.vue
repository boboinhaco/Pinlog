<template>
  <div v-if="result && form" class="review">
    <PageHero align="left" back="/home" title="링크 분석 결과"
              :sub="productOnly ? 'SNS 사진과 글에서 상품을 찾고, 인터넷 검색으로 상품명을 확인했어요.' : 'SNS 링크를 분석해 일정과 장소를 정리하고, 공식 공고와 비교했어요.'"
              doodle="좋아하는 콘텐츠가<br>새로운 일정이 되는 순간!" />
    <LinkBar :initial-url="result.original_url ?? ''" button-label="다른 링크 분석하기" compact class="lb" />

    <div class="cols">
      <!-- 원본 콘텐츠 -->
      <section class="card src-card">
        <div class="hd">
          <h2 class="section-title"><i class="sico" :style="{ background: source.color }"></i>원본 콘텐츠</h2>
          <a v-if="result.original_url" :href="result.original_url" target="_blank" rel="noopener" class="ghost-btn">↗ 새 창에서 보기</a>
        </div>
        <div class="post">
          <div class="who"><span class="av">{{ post.author.slice(0, 1).toUpperCase() }}</span><b>{{ post.author }}</b><small>{{ post.when }}</small></div>
          <div v-if="postImage && imgOk" class="pimg"><img :src="postImage" alt="원본 게시물 이미지" referrerpolicy="no-referrer" @error="imgOk = false" /></div>
          <div v-else class="pimg art"><CategoryArt :kind="category" fill /></div>
          <p class="cap"><b>{{ post.author }}</b>
            <template v-for="(t, i) in captionParts" :key="i"><span v-if="t.tag" class="ht">{{ t.text }}</span><template v-else>{{ t.text }}</template></template>
          </p>
          <p v-if="ex.demo" class="demo">예시 데이터로 만든 결과예요.</p>
        </div>
      </section>

      <!-- 추출된 정보 -->
      <section class="card info">
        <div class="hd">
          <h2 class="section-title"><Sparkles :size="22" />추출된 정보</h2>
          <small class="muted">AI가 콘텐츠를 분석하여 추출한 정보예요.</small>
        </div>
        <p v-if="ex.notice" class="notice"><Info :size="16" />{{ ex.notice }} <RouterLink :to="{ path: '/upload', query: { url: result.original_url } }">스크린샷 올리기 →</RouterLink></p>

        <input v-model="form.title" class="title-input" aria-label="제목" />
        <div class="cats" role="radiogroup" aria-label="저장할 카테고리">
          <button v-for="c in CATEGORIES" :key="c.key" type="button" role="radio" :aria-checked="category === c.key" class="tag"
                  :class="[`tone-${c.tone}`, { on: category === c.key }]" @click="category = c.key">{{ c.label }}</button>
        </div>

        <!-- 일정 (날짜 없는 상품 글은 생략) -->
        <div v-if="!productOnly" class="box">
          <div class="bh"><b><CalendarDays :size="17" />{{ dateKind === 'event_period' ? '행사 일정' : '신청 기간' }}</b><span class="tag" :class="`tone-${conf(dateKind).tone}`">{{ conf(dateKind).label }}</span></div>
          <div v-if="!multi" class="dates">
            <label class="dt"><small>시작일</small><input v-model="form.start" type="date" @change="form.touched = true" /></label>
            <span class="arrow">›</span>
            <label class="dt"><small>{{ dateKind === 'event_period' ? '종료일' : '마감일' }}</small><input v-model="form.end" type="date" :min="form.start || undefined" @change="form.touched = true" /></label>
            <span v-if="duration" class="dur">{{ duration }}</span>
          </div>
          <div v-else class="dates ro">
            <span class="dt"><small>시작일</small><b>{{ longDate(range.start) }}</b></span><span class="arrow">›</span>
            <span class="dt"><small>종료일</small><b>{{ longDate(range.end) }}</b></span>
            <span v-if="duration" class="dur">{{ duration }}</span>
          </div>
          <p class="note">{{ dateSourceNote }}</p>
        </div>

        <!-- 장소 -->
        <div v-if="places.length" class="box">
          <div class="bh"><b><MapPin :size="17" />추출된 장소 {{ places.length }}개</b><span class="tag" :class="`tone-${conf('location').tone}`">{{ conf('location').label }}</span></div>
          <div class="pl">
            <div class="mini-map"><PlaceMap :places="places.filter(p => p.lat != null)" height="100%" /></div>
            <ol>
              <li v-for="(p, n) in places" :key="p.name"><i>{{ n + 1 }}</i><span><b>{{ p.name }}</b><small>{{ p.address || p.event || '' }}</small></span></li>
            </ol>
          </div>
        </div>

        <!-- 여러 일정: 고르고 날짜 고치기 -->
        <div v-if="multi" class="box">
          <div class="bh"><b><ListChecks :size="17" />추출된 일정 {{ form.events.length }}개</b><small class="muted">{{ picked.length }}개 선택</small></div>
          <label v-for="(e, i) in form.events" :key="i" class="ev" :class="{ off: !e.on }">
            <input v-model="e.on" type="checkbox" />
            <input v-model="e.title" class="ev-title" aria-label="일정 이름" />
            <span class="ev-dates">
              <input v-model="e.start" type="date" aria-label="시작일" @change="e.touched = true" />~<input v-model="e.end" type="date" aria-label="종료일" @change="e.touched = true" />
            </span>
            <b v-if="e.ambiguous && !e.touched" class="tag tone-orange">날짜 확인</b>
          </label>
        </div>

        <!-- 사진·글에서 찾은 상품: 검색으로 확인한 이름 + 링크, 고른 것만 저장 -->
        <div v-if="form.products.length" class="box">
          <div class="bh"><b><ShoppingBag :size="17" />사진·글에서 찾은 상품 {{ form.products.length }}개</b><small class="muted">{{ pickedProducts.length }}개 선택</small></div>
          <p class="notice soft"><TriangleAlert :size="15" /><span>{{ productNotice }} <RouterLink v-if="!result.image_count && result.original_url" :to="{ path: '/upload', query: { url: result.original_url } }">장별 캡처 올리기 →</RouterLink></span></p>
          <label v-for="(p, i) in form.products" :key="i" class="pd" :class="{ off: !p.on }">
            <input v-model="p.on" type="checkbox" />
            <span class="pd-body">
              <span class="pd-top"><b>{{ p.matched_name || p.name }}</b><span class="tag" :class="`tone-${PRODUCT_CONF[p.confidence]?.tone ?? 'gray'}`">{{ PRODUCT_CONF[p.confidence]?.label ?? '확인 필요' }}</span></span>
              <small class="pd-sub">{{ productSub(p) }}</small>
              <small v-if="p.note" class="pd-note">{{ p.note }}</small>
              <span class="pd-links"><a v-for="l in p.links" :key="l.url" :href="l.url" target="_blank" rel="noopener" :class="l.kind" @click.stop>{{ LINK_KIND[l.kind] ?? '참고' }} · {{ host(l.url) }} ↗</a></span>
            </span>
          </label>
        </div>

        <!-- 타임라인 -->
        <div v-if="timeline.length > 1" class="box">
          <div class="bh"><b><GitCommitHorizontal :size="17" />예상 일정 타임라인</b><small class="muted">저장한 뒤 내 일정에서 더 자세히 고칠 수 있어요.</small></div>
          <div class="tl"><div v-for="(t, i) in timeline" :key="i" class="node"><small>{{ t.date }}</small><i></i><b>{{ t.label }}</b><small>{{ t.sub }}</small></div></div>
        </div>

        <p v-if="expired" class="warn red"><TriangleAlert :size="16" />이미 {{ expired }} 마감(종료)된 일정이에요. 기록용으로는 저장할 수 있어요.</p>
        <label v-if="needsDateCheck" class="warn check"><input v-model="dateChecked" type="checkbox" /> 날짜가 확실하지 않아요(연도·말일 추정). 날짜를 확인했어요.</label>
        <p v-if="error" class="err">{{ error.message }}</p>

        <div class="acts" :class="{ one: productOnly }">
          <button v-if="!productOnly" class="ghost" :disabled="saving || !canSave" @click="save('/calendar')"><CalendarPlus :size="18" />일정표에 추가하기</button>
          <button :disabled="saving || !canSave" @click="save(places.length ? '/map' : productOnly ? '/category/PRODUCT' : '/home')"><component :is="saving ? LoaderCircle : places.length ? MapPinned : Check" :size="18" :class="{ spin: saving }" />{{ saving ? '저장 중…' : places.length ? '지도에 저장하기' : '확인하고 저장하기' }}</button>
        </div>
      </section>
    </div>

    <!-- 공식 공고와 비교 (상품 글은 공고가 없으니 링크 내용 요약만) -->
    <section class="card cmp">
      <div class="hd">
        <h2 class="section-title">{{ productOnly ? '이 링크가 알려주는 내용' : '공식 공고와 비교' }} <span v-if="!productOnly" class="tag" :class="`tone-${GRADE[grade].tone}`">{{ GRADE[grade].label }}</span></h2>
      </div>
      <div class="sums" :class="{ one: productOnly }">
        <div><small>{{ productOnly ? '요약' : '이 링크가 알려주는 내용' }}</small><p>{{ ex.summary || '요약할 수 있는 내용이 없어요.' }}</p></div>
        <div v-if="!productOnly" class="off">
          <small>공식 공고에서는</small>
          <template v-if="primary">
            <p>{{ ver.official_summary }}</p>
            <a :href="primary.url" target="_blank" rel="noopener" class="srcl"><b>{{ primary.title || primary.url }}</b><span>{{ DOMAIN[primary.domain_type] ?? '출처' }} · {{ host(primary.url) }} ↗</span></a>
          </template>
          <p v-else class="muted">같은 내용을 다루는 공식 공고를 찾지 못했어요. 중요한 조건은 직접 한 번 더 확인해 주세요.</p>
        </div>
      </div>
      <CompareRows v-if="!productOnly && rows.length" :rows="rows" />
      <div v-if="ex.key_points?.length" class="kp"><b>그 밖의 정보</b><ul><li v-for="p in ex.key_points" :key="p">{{ p }}</li></ul></div>
    </section>
  </div>
  <p v-else-if="loadError" class="empty">{{ loadError }}</p>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getShareResult, confirmShareItems } from '../api/nexto'
import { CATEGORIES, CATEGORY, GRADE, DOMAIN_LABEL as DOMAIN, PRODUCT_CONF, LINK_KIND, PRODUCT_NOTICE, compareRows } from '../utils/labels'
import { longDate, periodLabel, ymd } from '../utils/events'
import { Sparkles, Info, CalendarDays, MapPin, MapPinned, ListChecks, GitCommitHorizontal, TriangleAlert, CalendarPlus, Check, LoaderCircle, ShoppingBag } from 'lucide-vue-next'
import { sourceOf } from '../utils/source'
import PageHero from '../components/PageHero.vue'
import LinkBar from '../components/LinkBar.vue'
import CompareRows from '../components/CompareRows.vue'
import CategoryArt from '../components/CategoryArt.vue'
import PlaceMap from '../components/PlaceMap.vue'

// 필드 확인 상태 → 신뢰도 배지
const CONF = { VERIFIED: { label: '높은 신뢰도', tone: 'green' }, REFINED: { label: '높은 신뢰도', tone: 'green' }, ADDED: { label: '공식 정보 추가', tone: 'purple' },
               CONFLICT: { label: '확인 필요', tone: 'red' }, AMBIGUOUS: { label: '보통 신뢰도', tone: 'orange' }, UNVERIFIED: { label: '공식 미확인', tone: 'gray' } }
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
// 상품만 있는 글(날짜·일정 없음)은 일정 입력·공고 비교 대신 상품 목록 위주로
const pickedProducts = computed(() => form.value.products.filter(p => p.on))
const productOnly = computed(() => category.value === 'PRODUCT' && !multi.value && !form.value.start && !form.value.end)
const productSub = p => [p.matched_name && p.matched_name !== p.name ? `게시물 표현: ${p.name}` : null, p.brand, p.kind, p.features, p.price_text && `게시물 가격 ${p.price_text}`].filter(Boolean).join(' · ')
// 링크만 넣으면 대표 사진 1장 기준이라 장별 캡처를 권함, 캡처를 올렸어도 추정이라는 점은 같음
const productNotice = computed(() => {
  const n = result.value.image_count ?? 0
  if (n) return `올려 주신 캡처 ${n}장을 기준으로 찾았어요. 그래도 상품 정보는 사진과 검색 결과로 추정한 것이라 실제와 다를 수 있으니, 구매 전에 직접 한 번 더 확인해 주세요.`
  if (result.value.original_url) return '링크만 넣으면 대표 사진(썸네일) 1장과 글만 읽을 수 있어요. 게시물이 여러 장이면 장별로 캡처한 사진을 올려 주시면 더 자세히 확인해요. 그래도 상품 정보는 추정이라 실제와 다를 수 있으니 구매 전에 직접 확인해 주세요.'
  return PRODUCT_NOTICE
})
const dateKind = computed(() => ex.value.category === 'EVENT' || (ex.value.event_period?.start && !ex.value.apply_period?.end) ? 'event_period' : 'apply_period')
const host = u => { try { return new URL(u).hostname.replace(/^www\./, '') } catch { return u } }
const conf = field => CONF[(ver.value.fields ?? []).find(f => f.field === field)?.status ?? 'UNVERIFIED']

// 원본 게시물: 인스타 미리보기 문구는 "작성자 - 날짜: "캡션"" 형식
const source = computed(() => sourceOf(result.value.original_url))
const post = computed(() => {
  const sp = result.value.source_post, desc = sp?.description ?? ''
  const m = desc.trim().match(/^(.+?) - (.+?): "([\s\S]*)"\.?$/)
  const created = result.value.created_at ? new Date(result.value.created_at) : null
  return {
    author: m?.[1] ?? (sp?.is_sns ? source.value.label : host(result.value.original_url ?? '') || source.value.label),
    when: m?.[2] ?? (created ? `${created.getMonth() + 1}월 ${created.getDate()}일 분석` : ''),
    caption: m?.[3] ?? ([sp?.title, desc].filter(Boolean).join('\n\n') || ex.value.summary || '')
  }
})
const postImage = computed(() => result.value.source_post?.image_url ?? ex.value.image_url)
const captionParts = computed(() => (' ' + post.value.caption).split(/(#[^\s#]+)/).map(t => ({ text: t, tag: t.startsWith('#') })))

// 장소: 여러 일정이면 선택한 일정의 장소들, 아니면 대표 장소
const places = computed(() => {
  const list = multi.value
    ? picked.value.filter(e => e.location?.name).map(e => ({ ...e.location, event: e.title }))
    : [ex.value.location ?? (official.value.location?.name ? official.value.location : null)].filter(l => l?.name)
  return [...new Map(list.map(p => [p.name, p])).values()]
})

// 전체 기간·기간 길이
const range = computed(() => {
  const s = picked.value.map(e => e.start).filter(Boolean).sort(), e = picked.value.map(x => x.end || x.start).filter(Boolean).sort()
  return { start: s[0], end: e.at(-1) }
})
const duration = computed(() => {
  const { start, end } = multi.value ? range.value : { start: form.value.start, end: form.value.end }
  if (!start || !end) return ''
  const n = Math.round((new Date(end + 'T00:00') - new Date(start + 'T00:00')) / 86400000)
  if (n < 0) return ''
  const days = n === 0 ? '하루' : `${n + 1}일간`
  return multi.value ? `${picked.value.length}개 일정 · ${days}` : days
})
const WD = ['일', '월', '화', '수', '목', '금', '토']
const short = s => { const d = new Date(s + 'T00:00'); return `${d.getMonth() + 1}.${d.getDate()} (${WD[d.getDay()]})` }
const timeline = computed(() => multi.value
  ? [...picked.value].filter(e => e.start).sort((a, b) => a.start.localeCompare(b.start)).map(e => ({ date: short(e.start), label: e.title, sub: e.location?.name ?? periodLabel(e.start, e.end) }))
  : [form.value.start && { date: short(form.value.start), label: dateKind.value === 'event_period' ? '시작' : '신청 시작', sub: '' },
     form.value.end && form.value.end !== form.value.start && { date: short(form.value.end), label: dateKind.value === 'event_period' ? '종료' : '마감', sub: '' }].filter(Boolean))

// 날짜 기본값: 공식 공고 값이 있으면 공식 기준, 없으면 SNS 기준
const officialPeriod = computed(() => official.value[dateKind.value]?.end || official.value[dateKind.value]?.start ? official.value[dateKind.value] : null)
const dateSourceNote = computed(() => multi.value ? '아래 목록에서 일정별 날짜를 고칠 수 있어요.' : form.value.touched ? '직접 입력한 날짜로 저장돼요.' : officialPeriod.value ? '공식 공고 기준 날짜로 채웠어요.' : (form.value.start || form.value.end) ? 'SNS 내용 기준 날짜예요.' : '날짜가 없으면 캘린더 대신 저장 목록에만 들어가요.')
const needsDateCheck = computed(() => multi.value ? picked.value.some(e => e.ambiguous && !e.touched) : form.value.ambiguous && !form.value.touched && (form.value.start || form.value.end))
// 마감일(없으면 시작일)이 모두 오늘보다 이전이면 경고
const expired = computed(() => {
  const ends = (multi.value ? picked.value.map(e => e.end || e.start) : [form.value.end || form.value.start]).filter(Boolean)
  const today = ymd(new Date()), past = ends.filter(d => d < today).sort()
  if (!past.length || past.length < ends.length) return null
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
                                         location: e.location, ambiguous: e.event_period?.status === 'ambiguous', touched: false })),
    products: (x.products ?? []).map(p => ({ ...p, on: true }))
  }
})

// 공식 값 우선으로 저장할 필드 구성 (장소는 좌표 있는 SNS 값 우선)
const pick = key => { const o = official.value[key], s = ex.value[key]; return (Array.isArray(o) ? o.length : o) ? o : s }
function buildItems() {
  const x = ex.value
  const products = pickedProducts.value.map(({ on, ...p }) => p)
  const common = { summary: x.summary, official_summary: ver.value.official_summary ?? null, key_points: x.key_points, image_url: postImage.value ?? x.image_url,
                   organization: x.organization, ...(products.length ? { products } : {}), ...(route.query.liked === '1' ? { liked: true } : {}) }
  if (multi.value) {
    // 일정이 여러 개면 상품은 첫 일정에만 붙여 중복 저장을 피함
    return picked.value.map((e, i) => ({
      title: e.title, category: category.value, user_overrides: e.touched || dateChecked.value ? ['event_period'] : [],
      fields: { ...common, ...(i ? { products: undefined } : {}), event_period: { start: e.start || null, end: e.end || e.start || null, status: 'exact' }, location: e.location }
    }))
  }
  const f = form.value
  return [{
    title: f.title, category: category.value, user_overrides: f.touched || dateChecked.value ? [dateKind.value] : [],
    fields: { ...common, target: pick('target'), eligibility: pick('eligibility'), benefit_amount: pick('benefit_amount'), requirements: pick('requirements'),
              location: x.location?.lat != null ? x.location : pick('location'),
              [dateKind.value]: f.start || f.end ? { start: f.start || f.end, end: f.end || f.start, status: 'exact' } : null }
  }]
}

async function save(to) {
  saving.value = true; error.value = null
  try {
    const saved = await confirmShareItems(route.params.shareId, buildItems())
    const first = saved.map(i => i.fields.event_period?.start ?? i.fields.apply_period?.start ?? i.fields.apply_period?.end).filter(Boolean).sort()[0]
    router.push({ path: to, query: to === '/calendar' && first ? { month: first.slice(0, 7) } : to === '/home' ? { added: saved.length } : {} })
  } catch (e) { error.value = e } finally { saving.value = false }
}
</script>

<style scoped>
.review { display: grid; gap: 16px; }
.lb { max-width: 980px; width: 100%; margin: 0 auto; }
.cols { display: grid; grid-template-columns: .85fr 1.15fr; gap: 18px; align-items: start; }
.card { margin: 0; padding: 20px 22px; }
.hd { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 12px; }
.hd .section-title { margin: 0; }
.muted { color: var(--muted); font-size: 13px; }
.sico { display: inline-block; width: 26px; height: 26px; border-radius: 8px; }
.ghost-btn { padding: 6px 12px; border: 1px solid var(--line); border-radius: 10px; font-size: 13px; text-decoration: none; color: var(--accent-deep); }
.ghost-btn:hover { background: var(--hover); }
.post { border-top: 1px solid var(--line); padding-top: 12px; }
.who { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.av { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 50%; background: var(--cta); color: #fff; font-weight: 700; }
.who small { color: var(--faint); font-size: 12.5px; }
.pimg { border-radius: 12px; overflow: hidden; background: var(--soft); }
.pimg img { width: 100%; max-height: 420px; object-fit: cover; display: block; }
.pimg.art { aspect-ratio: 4 / 3; }
.pimg.art :deep(svg) { width: 100%; height: 100%; display: block; }
.cap { margin: 12px 0 0; font-size: 14px; line-height: 1.7; white-space: pre-line; max-height: 260px; overflow-y: auto; }
.cap b { margin-right: 4px; }
.ht { color: var(--accent-deep); }
.demo { margin: 10px 0 0; font-size: 12.5px; color: var(--faint); }
.notice { display: flex; align-items: center; gap: 8px; margin: 0 0 10px; padding: 10px 14px; border-radius: 10px; background: var(--t-yellow); color: #6f5316; font-size: 13.5px; }
.notice a { color: #9a6a12; font-weight: 600; }
.notice.soft { align-items: flex-start; background: var(--t-orange); color: #8a4a12; font-size: 13px; line-height: 1.5; }
.notice.soft .lucide { flex: none; margin-top: 2px; }
.notice.soft a { color: #8a4a12; font-weight: 700; white-space: nowrap; }
.pd { display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: start; padding: 10px 0; border-bottom: 1px solid var(--line); cursor: pointer; }
.pd:last-of-type { border-bottom: 0; }
.pd.off { opacity: .45; }
.pd input { width: 18px; height: 18px; margin-top: 2px; accent-color: var(--accent); }
.pd-body { display: grid; gap: 4px; min-width: 0; }
.pd-top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.pd-top b { font-size: 14.5px; }
.pd-sub { font-size: 12.5px; color: var(--muted); }
.pd-note { font-size: 12.5px; color: #8a4a12; }
.pd-links { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
.pd-links a { padding: 3px 10px; border-radius: 999px; border: 1px solid var(--line-strong); background: #fff; font-size: 12px; text-decoration: none; color: var(--ink); }
.pd-links a.official { border-color: var(--accent); color: var(--accent); font-weight: 600; }
.pd-links a.shop { color: var(--accent-deep); }
.pd-links a.search { color: var(--muted); }
.pd-links a:hover { background: var(--hover); }
.acts.one, .sums.one { grid-template-columns: 1fr; }
.title-input { padding: 4px 8px; margin-left: -8px; border: 0; border-radius: 8px; background: none; font-size: 22px; font-weight: 800; }
.title-input:hover, .title-input:focus { background: var(--soft); outline: none; }
.cats { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 14px; }
.cats .tag { border: 1.5px solid transparent; cursor: pointer; padding: 3px 11px; font-size: 12.5px; opacity: .75; }
.cats .tag.on { opacity: 1; border-color: currentColor; font-weight: 700; }
.box { padding: 14px 16px; margin-bottom: 12px; border: 1px solid var(--line); border-radius: 14px; background: #fbfcff; }
.bh { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; margin-bottom: 10px; }
.bh b { display: inline-flex; align-items: center; gap: 7px; font-size: 15px; }
.bh .lucide { color: var(--accent); }
.bh .muted { margin-left: auto; }
.dates { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.dt { flex: 1; min-width: 150px; display: grid; gap: 2px; padding: 8px 12px; border-radius: 12px; background: #fff; border: 1px solid var(--line); }
.dt small { font-size: 12px; color: var(--muted); }
.dt input { border: 0; padding: 0; font-size: 15px; font-weight: 700; background: none; }
.dt input:focus { outline: none; }
.dt b { font-size: 15px; }
.arrow { color: var(--faint); font-size: 20px; }
.dur { padding: 10px 18px; border-radius: 999px; background: var(--accent-soft); color: var(--accent-deep); font-weight: 700; }
.note { margin: 8px 0 0; font-size: 12.5px; color: var(--muted); }
.pl { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.mini-map { height: 190px; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }
ol { margin: 0; padding: 0; list-style: none; display: grid; align-content: start; gap: 6px; max-height: 190px; overflow-y: auto; }
ol li { display: flex; align-items: center; gap: 10px; padding: 6px 4px; border-bottom: 1px solid var(--line); }
ol li:last-child { border-bottom: 0; }
ol i { flex: none; display: grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; background: var(--accent); color: #fff; font-style: normal; font-size: 12px; font-weight: 700; }
ol span { display: grid; min-width: 0; }
ol b { font-size: 14px; }
ol small { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ev { display: grid; grid-template-columns: auto 1fr auto auto; gap: 10px; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--line); cursor: pointer; }
.ev:last-of-type { border-bottom: 0; }
.ev.off { opacity: .45; }
.ev input[type=checkbox], .check input { width: 18px; height: 18px; accent-color: var(--accent); }
.ev-title { border: 0; padding: 2px 0; background: none; font-weight: 700; font-size: 14px; }
.ev-dates { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--muted); }
.ev-dates input { width: 136px; padding: 4px 6px; font-size: 13px; }
.tl { position: relative; display: grid; grid-auto-flow: column; grid-auto-columns: minmax(90px, 1fr); overflow-x: auto; padding: 4px 0; }
.tl::before { content: ''; position: absolute; left: 40px; right: 40px; top: 32px; border-top: 2px solid var(--line-strong); }
.node { position: relative; display: grid; justify-items: center; gap: 4px; text-align: center; padding: 0 4px; }
.node i { width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 3px solid var(--accent); }
.node b { font-size: 12.5px; line-height: 1.3; }
.node small { font-size: 11.5px; color: var(--muted); }
.warn { display: flex; align-items: center; gap: 8px; margin: 0 0 10px; padding: 10px 14px; border-radius: 10px; font-size: 13.5px; }
.warn.red { background: var(--t-red); color: #a8322d; }
.warn.check { background: var(--t-yellow); color: #6f5316; cursor: pointer; }
.err { margin: 0 0 10px; color: var(--i-red); font-size: 14px; }
.acts { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 4px; }
.acts button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; height: 50px; border-radius: 14px; font-size: 15.5px; }
.acts .spin { animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.acts button:not(.ghost) { background: var(--cta); box-shadow: 0 6px 16px rgba(74, 114, 216, .25); }
.acts .ghost { color: var(--accent-deep); border-color: var(--line-strong); }
.cmp .section-title .tag { margin-left: 6px; }
.sums { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.sums > div { padding: 14px 16px; border-radius: 12px; background: var(--soft); }
.sums small { font-size: 12px; font-weight: 700; color: var(--muted); }
.sums p { margin: 4px 0 0; font-size: 14px; line-height: 1.7; }
.off { background: var(--accent-soft) !important; }
.srcl { display: grid; margin-top: 10px; padding: 10px 12px; border-radius: 10px; background: #fff; text-decoration: none; font-size: 13px; }
.srcl span { color: var(--muted); font-size: 12px; }
.kp { margin-top: 14px; font-size: 14px; }
.kp ul { margin: 6px 0 0; padding-left: 20px; line-height: 1.8; }
@media (max-width: 1150px) { .cols { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .pl, .sums, .acts { grid-template-columns: 1fr; }
  .ev { grid-template-columns: auto 1fr; }
  .ev-dates, .ev .tag { grid-column: 2; }
  .ev-dates input { width: 100%; }
}
</style>
