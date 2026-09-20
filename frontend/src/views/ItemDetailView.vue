<template>
  <section v-if="item" class="detail">
    <!-- 카테고리로 돌아가기 -->
    <div class="top">
      <RouterLink :to="`/category/${cat.key}`" class="back" :class="`tone-${cat.tone}`"><ChevronLeft :size="20" :stroke-width="2.6" />{{ cat.label }}</RouterLink>
    </div>

    <!-- 제목 영역 -->
    <header class="head">
      <div class="thumb">
        <img v-if="f.image_url && imgOk" :src="f.image_url" alt="" referrerpolicy="no-referrer" @error="imgOk = false" />
        <CategoryArt v-else :kind="item.category" fill />
      </div>
      <div class="head-body">
        <div class="chips">
          <span class="tag" :class="`tone-${GRADE[item.overall_grade]?.tone ?? 'gray'}`">{{ GRADE[item.overall_grade]?.label ?? item.overall_grade }}</span>
          <span v-if="dday" class="tag" :class="dday === '종료' ? 'tone-gray' : 'tone-red'">{{ dday }}</span>
          <span v-if="f.organization" class="org">{{ f.organization }}</span>
        </div>
        <h1>{{ item.title }}</h1>
        <div class="acts">
          <label class="move">카테고리
            <select :value="item.category" @change="move($event.target.value)">
              <option v-for="c in CATEGORIES" :key="c.key" :value="c.key">{{ c.label }}</option>
            </select>
          </label>
          <button class="ghost sm" @click="remove"><Trash2 :size="15" />삭제</button>
          <span v-if="saved" class="ok"><Check :size="15" />저장됨</span>
        </div>
      </div>
    </header>

    <div class="cols">
      <!-- 원본 콘텐츠 -->
      <section class="card">
        <div class="hd">
          <h2 class="section-title"><i class="sico" :style="{ background: source.color }"></i>원본 콘텐츠</h2>
          <a v-if="f.source_url" :href="f.source_url" target="_blank" rel="noopener" class="ghost-btn">↗ 새 창에서 보기</a>
        </div>
        <div class="post">
          <div class="who"><span class="av">{{ source.label.slice(0, 1).toUpperCase() }}</span><b>{{ source.label }}</b><small>{{ savedWhen }}</small></div>
          <div v-if="f.image_url && imgOk" class="pimg"><img :src="f.image_url" alt="원본 게시물 이미지" referrerpolicy="no-referrer" @error="imgOk = false" /></div>
          <div v-else class="pimg art"><CategoryArt :kind="item.category" fill /></div>
          <p class="cap">{{ f.summary || 'SNS 요약이 없는 항목이에요. 직접 추가했거나 링크에서 읽을 내용이 없었어요.' }}</p>
        </div>
      </section>

      <!-- 저장된 정보 -->
      <section class="card info">
        <div class="hd">
          <h2 class="section-title"><Sparkles :size="22" />저장된 정보</h2>
          <small class="muted">확인하고 저장한 내용이에요.</small>
        </div>

        <!-- 일정 -->
        <div v-if="period.start || period.end" class="box">
          <div class="bh"><b><CalendarDays :size="17" />{{ f.event_period ? '행사 일정' : '신청 기간' }}</b><span v-if="dday" class="tag" :class="dday === '종료' ? 'tone-gray' : 'tone-red'">{{ dday }}</span></div>
          <div class="dates">
            <span class="dt"><small>시작일</small><b>{{ longDate(period.start || period.end) }}</b></span>
            <span class="arrow">›</span>
            <span class="dt"><small>{{ f.event_period ? '종료일' : '마감일' }}</small><b>{{ longDate(period.end || period.start) }}</b></span>
            <span v-if="duration" class="dur">{{ duration }}</span>
          </div>
        </div>

        <!-- 대상 · 자격 -->
        <div v-if="display(f.target) || f.eligibility?.length" class="box">
          <div class="bh"><b><Users :size="17" />대상 · 자격요건</b></div>
          <dl>
            <template v-if="display(f.target)"><dt>대상</dt><dd>{{ display(f.target) }}</dd></template>
            <template v-if="f.eligibility?.length"><dt>자격요건</dt><dd><ul><li v-for="e in f.eligibility" :key="e">{{ e }}</li></ul></dd></template>
          </dl>
        </div>

        <!-- 혜택 · 서류 -->
        <div v-if="display(f.benefit_amount) || f.requirements?.length" class="box">
          <div class="bh"><b><Gift :size="17" />혜택 · 준비 서류</b></div>
          <dl>
            <template v-if="display(f.benefit_amount)"><dt>혜택</dt><dd>{{ display(f.benefit_amount) }}</dd></template>
            <template v-if="f.requirements?.length"><dt>준비 서류</dt><dd>{{ f.requirements.join(', ') }}</dd></template>
          </dl>
        </div>

        <!-- 장소 -->
        <div v-if="f.location?.name" class="box">
          <div class="bh"><b><MapPin :size="17" />장소</b></div>
          <div class="pl" :class="{ nomap: f.location.lat == null }">
            <div v-if="f.location.lat != null" class="mini-map"><PlaceMap :places="[f.location]" height="100%" /></div>
            <div class="addr"><b>{{ f.location.name }}</b><small v-if="f.location.address">{{ f.location.address }}</small></div>
          </div>
        </div>

        <!-- 상품 -->
        <div v-if="f.products?.length" class="box">
          <div class="bh"><b><ShoppingBag :size="17" />저장한 상품 {{ f.products.length }}개</b></div>
          <p class="notice"><TriangleAlert :size="15" /><span>{{ PRODUCT_NOTICE }}</span></p>
          <div v-for="p in f.products" :key="p.name" class="pd">
            <span class="pd-top"><b>{{ p.matched_name || p.name }}</b><span class="tag" :class="`tone-${PRODUCT_CONF[p.confidence]?.tone ?? 'gray'}`">{{ PRODUCT_CONF[p.confidence]?.label ?? '확인 필요' }}</span></span>
            <small class="pd-sub">{{ productSub(p) }}</small>
            <small v-if="p.note" class="pd-note">{{ p.note }}</small>
            <span class="pd-links"><a v-for="l in p.links" :key="l.url" :href="l.url" target="_blank" rel="noopener" :class="l.kind">{{ LINK_KIND[l.kind] ?? '참고' }} · {{ host(l.url) }} ↗</a></span>
          </div>
        </div>

        <p v-if="!hasAny" class="empty">저장된 세부 정보가 없어요.</p>
      </section>
    </div>

    <!-- 공식 공고와 비교 (상품만 있는 항목은 요약만) -->
    <section class="card cmp">
      <div class="hd">
        <h2 class="section-title">{{ productOnly ? '이 링크가 알려주는 내용' : '공식 공고와 비교' }} <span v-if="!productOnly" class="tag" :class="`tone-${GRADE[item.overall_grade]?.tone ?? 'gray'}`">{{ GRADE[item.overall_grade]?.label ?? item.overall_grade }}</span></h2>
      </div>
      <div class="sums" :class="{ one: productOnly }">
        <div><small>{{ productOnly ? '요약' : 'SNS 링크가 알려주는 내용' }}</small><p>{{ f.summary || '요약할 수 있는 내용이 없어요.' }}</p></div>
        <div v-if="!productOnly" class="off">
          <small>공식 공고에서는</small>
          <template v-if="item.source">
            <p>{{ item.official_summary || f.official_summary || '공식 출처를 찾았어요. 아래 링크에서 자세한 내용을 확인해 주세요.' }}</p>
            <a :href="item.source.url" target="_blank" rel="noopener" class="srcl"><b>{{ item.source.title || item.source.url }}</b><span>{{ DOMAIN_LABEL[item.source.domain_type] ?? '출처' }} · {{ host(item.source.url) }} ↗</span></a>
          </template>
          <p v-else class="muted">같은 내용을 다루는 공식 공고를 찾지 못했어요. 중요한 조건은 직접 한 번 더 확인해 주세요.</p>
        </div>
      </div>
      <CompareRows v-if="!productOnly && rows.length" :rows="rows" />
      <div v-if="f.key_points?.length" class="kp"><b>그 밖의 정보</b><ul><li v-for="p in f.key_points" :key="p">{{ p }}</li></ul></div>
    </section>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getItem, patchItem, deleteItem } from '../api/nexto'
import { longDate } from '../utils/events'
import { sourceOf } from '../utils/source'
import { ChevronLeft, Trash2, Check, Sparkles, CalendarDays, Users, Gift, MapPin, ShoppingBag, TriangleAlert } from 'lucide-vue-next'
import { CATEGORIES, CATEGORY, GRADE, DOMAIN_LABEL, PRODUCT_CONF, LINK_KIND, PRODUCT_NOTICE, display, compareRows } from '../utils/labels'
import CategoryArt from '../components/CategoryArt.vue'
import PlaceMap from '../components/PlaceMap.vue'
import CompareRows from '../components/CompareRows.vue'

const route = useRoute(), router = useRouter(), item = ref(null), imgOk = ref(true), saved = ref(false)
const f = computed(() => item.value.fields ?? {})
const cat = computed(() => CATEGORY[item.value.category] ?? CATEGORY.OTHER)
const source = computed(() => sourceOf(f.value.source_url))
const period = computed(() => f.value.event_period ?? f.value.apply_period ?? {})
const rows = computed(() => compareRows(f.value, item.value.verification_fields ?? []))
const hasFacts = computed(() => period.value.start || period.value.end || display(f.value.target) || f.value.eligibility?.length || display(f.value.benefit_amount) || f.value.location?.name)
const hasAny = computed(() => hasFacts.value || f.value.products?.length)
const productOnly = computed(() => !!f.value.products?.length && !hasFacts.value)
const host = u => { try { return new URL(u).hostname.replace(/^www\./, '') } catch { return u } }
const productSub = p => [p.matched_name && p.matched_name !== p.name ? `게시물 표현: ${p.name}` : null, p.brand, p.kind, p.features, p.price_text && `게시물 가격 ${p.price_text}`].filter(Boolean).join(' · ')
const savedWhen = computed(() => { const d = new Date(item.value.created_at); return `${d.getMonth() + 1}월 ${d.getDate()}일 저장` })

// 기간 길이 · 마감(또는 시작)까지 남은 날
const duration = computed(() => {
  const { start, end } = period.value
  if (!start || !end) return ''
  const n = Math.round((new Date(end + 'T00:00') - new Date(start + 'T00:00')) / 86400000)
  return n < 0 ? '' : n === 0 ? '하루' : `${n + 1}일간`
})
const dday = computed(() => {
  const target = period.value.end || period.value.start
  if (!target) return null
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const diff = Math.round((new Date(target + 'T00:00') - today) / 86400000)
  return diff > 0 ? `D-${diff}` : diff === 0 ? 'D-DAY' : '종료'
})
onMounted(async () => (item.value = await getItem(route.params.itemId)))

async function move(category) {
  await patchItem(item.value.item_id, { category }); item.value.category = category
  saved.value = true; setTimeout(() => (saved.value = false), 1500)
}
async function remove() {
  if (!confirm(`'${item.value.title}'을(를) 삭제할까요? 캘린더에서도 사라져요.`)) return
  await deleteItem(item.value.item_id); router.push(`/category/${item.value.category ?? 'OTHER'}`)
}
</script>

<style scoped>
.detail { display: grid; gap: 16px; padding-top: 8px; }
.top { display: flex; align-items: center; }
.back { display: inline-flex; align-items: center; gap: 2px; padding: 7px 16px 7px 8px; border-radius: 999px; font-size: 15px; font-weight: 700; text-decoration: none; transition: box-shadow .15s, transform .15s; }
.back:hover { box-shadow: var(--shadow); transform: translateX(-2px); }
/* 제목 */
.head { display: flex; gap: 20px; align-items: center; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
.thumb { flex: none; width: 160px; aspect-ratio: 5 / 4; border-radius: 14px; overflow: hidden; border: 1px solid var(--line); background: var(--soft); }
.thumb img, .thumb :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.head-body { min-width: 0; }
.head h1 { margin: 6px 0 10px; font-size: clamp(22px, 3vw, 30px); letter-spacing: -.03em; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.org { font-size: 14px; color: var(--muted); }
.acts { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; }
.move { display: flex; align-items: center; gap: 6px; color: var(--muted); }
.move select { width: auto; padding: 5px 10px; font-size: 13px; }
.acts .sm { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; font-size: 13px; }
.ok { display: inline-flex; align-items: center; gap: 4px; color: var(--mint-ink); }
/* 카드 공통 (검토 화면과 같은 구성) */
.cols { display: grid; grid-template-columns: .85fr 1.15fr; gap: 18px; align-items: start; }
.card { margin: 0; padding: 20px 22px; }
.hd { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 12px; }
.hd .section-title { margin: 0; }
.muted { color: var(--muted); font-size: 13px; margin: 0; }
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
.cap { margin: 12px 0 0; font-size: 14px; line-height: 1.7; white-space: pre-line; }
.box { padding: 14px 16px; margin-bottom: 12px; border: 1px solid var(--line); border-radius: 14px; background: #fbfcff; }
.box:last-child { margin-bottom: 0; }
.bh { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; margin-bottom: 10px; }
.bh b { display: inline-flex; align-items: center; gap: 7px; font-size: 15px; }
.bh .lucide { color: var(--accent); }
.dates { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.dt { flex: 1; min-width: 150px; display: grid; gap: 2px; padding: 8px 12px; border-radius: 12px; background: #fff; border: 1px solid var(--line); }
.dt small { font-size: 12px; color: var(--muted); }
.dt b { font-size: 15px; }
.arrow { color: var(--faint); font-size: 20px; }
.dur { padding: 10px 18px; border-radius: 999px; background: var(--accent-soft); color: var(--accent-deep); font-weight: 700; }
dl { display: grid; grid-template-columns: 84px 1fr; gap: 8px 14px; margin: 0; }
dt { color: var(--muted); font-size: 14px; }
dd { margin: 0; line-height: 1.6; font-size: 14.5px; }
dd ul { margin: 0; padding-left: 18px; }
.pl { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: center; }
.pl.nomap { grid-template-columns: 1fr; }
.mini-map { height: 190px; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }
.addr { display: grid; gap: 4px; }
.addr b { font-size: 15px; }
.addr small { font-size: 13px; color: var(--muted); }
.empty { padding: 20px 0; }
/* 상품 */
.notice { display: flex; align-items: flex-start; gap: 8px; margin: 0 0 8px; padding: 10px 14px; border-radius: 10px; background: var(--t-orange); color: #8a4a12; font-size: 13px; line-height: 1.5; }
.notice .lucide { flex: none; margin-top: 2px; }
.pd { display: grid; gap: 4px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.pd:last-child { border-bottom: 0; padding-bottom: 2px; }
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
/* 공식 비교 */
.cmp .section-title .tag { margin-left: 6px; }
.sums { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.sums.one { grid-template-columns: 1fr; }
.sums > div { padding: 14px 16px; border-radius: 12px; background: var(--soft); }
.sums small { font-size: 12px; font-weight: 700; color: var(--muted); }
.sums p { margin: 4px 0 0; font-size: 14px; line-height: 1.7; }
.off { background: var(--accent-soft) !important; }
.srcl { display: grid; margin-top: 10px; padding: 10px 12px; border-radius: 10px; background: #fff; text-decoration: none; font-size: 13px; }
.srcl span { color: var(--muted); font-size: 12px; }
.kp { margin-top: 14px; font-size: 14px; }
.kp ul { margin: 6px 0 0; padding-left: 20px; line-height: 1.8; }
@media (max-width: 1150px) { .cols { grid-template-columns: 1fr; } }
@media (max-width: 760px) {
  .head { flex-direction: column; align-items: flex-start; }
  .thumb { width: 100%; aspect-ratio: 5 / 2; }
  .pl, .sums { grid-template-columns: 1fr; }
  dl { grid-template-columns: 1fr; gap: 2px; }
  dd { margin-bottom: 8px; }
}
</style>
