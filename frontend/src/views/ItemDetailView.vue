<template>
  <section v-if="item" class="detail">
    <RouterLink :to="`/category/${item.category ?? 'OTHER'}`" class="back">‹ {{ CATEGORY_LABEL[item.category] ?? '기타' }}</RouterLink>

    <div class="head">
      <div class="thumb">
        <img v-if="f.image_url && imgOk" :src="f.image_url" alt="" referrerpolicy="no-referrer" @error="imgOk = false" />
        <CategoryArt v-else :kind="item.category" fill />
      </div>
      <div class="head-body">
        <div class="chips">
          <span class="tag" :class="`tone-${GRADE[item.overall_grade]?.tone ?? 'gray'}`">{{ GRADE[item.overall_grade]?.label ?? item.overall_grade }}</span>
          <span v-if="f.organization" class="muted">{{ f.organization }}</span>
        </div>
        <h1>{{ item.title }}</h1>
        <div class="acts">
          <label class="move">카테고리
            <select :value="item.category" @change="move($event.target.value)">
              <option v-for="c in CATEGORIES" :key="c.key" :value="c.key">{{ c.label }}</option>
            </select>
          </label>
          <button class="ghost" @click="remove">삭제</button>
          <span v-if="saved" class="ok">✓ 저장됨</span>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card facts">
        <h2 class="panel-title">한눈에 보기</h2>
        <dl>
          <template v-if="period.start || period.end"><dt>{{ f.event_period ? '행사 기간' : '신청 기간' }}</dt><dd>{{ periodText }}<b v-if="dday" class="dday">{{ dday }}</b></dd></template>
          <template v-if="display(f.target)"><dt>대상</dt><dd>{{ display(f.target) }}</dd></template>
          <template v-if="f.eligibility?.length"><dt>자격요건</dt><dd><ul><li v-for="e in f.eligibility" :key="e">{{ e }}</li></ul></dd></template>
          <template v-if="display(f.benefit_amount)"><dt>혜택</dt><dd>{{ display(f.benefit_amount) }}</dd></template>
          <template v-if="f.requirements?.length"><dt>준비 서류</dt><dd>{{ f.requirements.join(', ') }}</dd></template>
          <template v-if="f.location?.name"><dt>장소</dt><dd>{{ display(f.location) }}</dd></template>
        </dl>
        <p v-if="!hasFacts" class="muted">저장된 세부 정보가 없어요.</p>
      </div>

      <div class="side">
        <div v-if="f.summary || item.official_summary" class="card">
          <h2 class="panel-title">요약</h2>
          <p v-if="item.official_summary" class="sum"><b>공식 공고</b>{{ item.official_summary }}</p>
          <p v-if="f.summary" class="sum"><b>SNS 링크</b>{{ f.summary }}</p>
        </div>
        <div class="card links">
          <a v-if="item.source" :href="item.source.url" target="_blank" rel="noopener"><b>공식 출처</b>{{ item.source.title || item.source.url }} ↗</a>
          <a v-if="f.source_url" :href="f.source_url" target="_blank" rel="noopener"><b>원본 SNS</b>게시물 열기 ↗</a>
          <p v-if="!item.source" class="muted">공식 출처를 찾지 못한 항목이에요. 중요한 조건은 직접 확인해 주세요.</p>
        </div>
      </div>
    </div>

    <PlaceMap v-if="f.location?.lat != null" :places="[f.location]" height="240px" class="place-map" />

    <div v-if="f.key_points?.length" class="card">
      <h2 class="panel-title">그 밖의 정보</h2>
      <ul class="points"><li v-for="p in f.key_points" :key="p">{{ p }}</li></ul>
    </div>

    <div v-if="item.verification_fields.length" class="card">
      <h2 class="panel-title">SNS와 공식 공고 비교</h2>
      <CompareRows :rows="compareRows(f, item.verification_fields)" />
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getItem, patchItem, deleteItem } from '../api/nexto'
import { longDate } from '../utils/events'
import { CATEGORIES, CATEGORY_LABEL, GRADE, display, compareRows } from '../utils/labels'
import CategoryArt from '../components/CategoryArt.vue'
import PlaceMap from '../components/PlaceMap.vue'
import CompareRows from '../components/CompareRows.vue'

const route = useRoute(), router = useRouter(), item = ref(null), imgOk = ref(true), saved = ref(false)
const f = computed(() => item.value.fields ?? {})
const period = computed(() => f.value.event_period ?? f.value.apply_period ?? {})
const periodText = computed(() => { const { start, end } = period.value; return start && end && start !== end ? `${longDate(start)} ~ ${longDate(end)}` : longDate(end || start) })
const hasFacts = computed(() => period.value.start || period.value.end || display(f.value.target) || f.value.eligibility?.length || display(f.value.benefit_amount) || f.value.location?.name)

// 마감(또는 시작)까지 남은 날
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
.detail { display: grid; gap: 14px; padding-top: 16px; }
.detail .card { margin: 0; }
.back { color: var(--faint); text-decoration: none; font-size: 14px; }
.head { display: flex; gap: 20px; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--line); }
.thumb { flex: none; width: 150px; aspect-ratio: 5 / 4; border-radius: 6px; overflow: hidden; border: 1px solid var(--line); }
.thumb img, .thumb :deep(svg) { width: 100%; height: 100%; object-fit: cover; display: block; }
.head-body { min-width: 0; }
.head h1 { margin: 6px 0 10px; font-size: clamp(22px, 3vw, 30px); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.acts { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; }
.move { display: flex; align-items: center; gap: 6px; color: var(--muted); }
.move select { width: auto; padding: 4px 8px; font-size: 13px; }
.acts .ghost { padding: 4px 10px; font-size: 13px; }
.ok { color: var(--mint-ink); }
.muted { color: var(--muted); font-size: 14px; margin: 0; }
.grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 14px; align-items: start; }
.side { display: grid; gap: 14px; }
dl { display: grid; grid-template-columns: 96px 1fr; gap: 12px 16px; margin: 0; }
dt { color: var(--muted); font-size: 14px; }
dd { margin: 0; line-height: 1.6; }
dd ul { margin: 0; padding-left: 18px; }
.dday { margin-left: 8px; padding: 1px 7px; border-radius: 4px; background: var(--t-red); color: #a8322d; font-size: 12px; font-weight: 500; }
.sum { margin: 0 0 12px; line-height: 1.7; }
.sum b { display: block; font-size: 12px; color: var(--muted); margin-bottom: 2px; font-weight: 500; }
.links { display: grid; gap: 8px; }
.links a { display: block; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px; text-decoration: none; font-size: 14px; }
.links a:hover { background: var(--hover); }
.links b { display: block; font-size: 12px; color: var(--muted); margin-bottom: 2px; font-weight: 500; }
.points { margin: 0; padding-left: 20px; line-height: 1.9; }
.place-map { border: 1px solid var(--line); }
@media (max-width: 760px) {
  .head { flex-direction: column; align-items: flex-start; }
  .thumb { width: 100%; aspect-ratio: 5 / 2; }
  .grid { grid-template-columns: 1fr; }
  dl { grid-template-columns: 1fr; gap: 2px; }
  dd { margin-bottom: 10px; }
}
</style>
