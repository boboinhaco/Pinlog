<template>
  <ModalSheet :title="TITLE[mode]" @close="emit('close')">
    <form class="ed" @submit.prevent="save">
      <template v-if="mode === 'new'">
        <label>일정 이름<input v-model="f.title" required maxlength="200" placeholder="예: 성수 팝업스토어 방문" /></label>
        <label>카테고리
          <select v-model="f.category"><option v-for="c in CATEGORIES" :key="c.key" :value="c.key">{{ c.label }}</option></select>
        </label>
      </template>
      <div v-if="mode !== 'place'" class="two">
        <label>시작일<input v-model="f.start" type="date" :required="mode === 'date'" /></label>
        <label>종료일 (마감일)<input v-model="f.end" type="date" :min="f.start || undefined" /></label>
      </div>
      <template v-if="mode !== 'date'">
        <label>장소 이름<input v-model="f.place" :required="mode === 'place'" placeholder="예: 노들섬" /></label>
        <label>주소 (선택)<input v-model="f.address" placeholder="주소를 적으면 지도 위치가 더 정확해요" /></label>
      </template>
      <p v-if="error" class="err">{{ error }}</p>
      <div class="acts">
        <button type="button" class="ghost" @click="emit('close')">취소</button>
        <button :disabled="busy">{{ busy ? '저장 중…' : '저장' }}</button>
      </div>
    </form>
  </ModalSheet>
</template>

<script setup>
import { ref } from 'vue'
import { createManualItem, patchItem } from '../api/nexto'
import { CATEGORIES } from '../utils/labels'
import ModalSheet from './ModalSheet.vue'

// mode: new(새 일정) | date(날짜 넣기·수정) | place(장소 넣기)
const props = defineProps({ mode: { type: String, default: 'new' }, item: Object, date: String })
const emit = defineEmits(['close', 'saved'])
const TITLE = { new: '새 일정 추가', date: '일정 날짜', place: '장소 저장' }
const it = props.item
const f = ref({
  title: '', category: 'EVENT', start: it?.start ?? props.date ?? '', end: it?.end ?? props.date ?? '',
  place: it?.place?.name ?? '', address: it?.place?.address ?? ''
})
const busy = ref(false), error = ref('')

async function save() {
  busy.value = true; error.value = ''
  const v = f.value, period = v.start || v.end ? { start: v.start || v.end, end: v.end || v.start, status: 'exact' } : null
  const location = v.place.trim() ? { name: v.place.trim(), address: v.address.trim() || null } : null
  try {
    let saved
    if (props.mode === 'new') saved = await createManualItem({ title: v.title, category: v.category, fields: { event_period: period, location } })
    // 기존 항목의 날짜 종류(신청 기간/행사 기간)는 유지
    else if (props.mode === 'date') saved = await patchItem(it.id, { fields: { [it.periodKey ?? 'event_period']: period } })
    else saved = await patchItem(it.id, { fields: { location } })
    emit('saved', saved)
  } catch (e) { error.value = e.message } finally { busy.value = false }
}
</script>

<style scoped>
.ed { display: grid; gap: 12px; }
label { display: grid; gap: 4px; font-size: 13px; font-weight: 600; color: var(--muted); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.err { margin: 0; color: var(--i-red); font-size: 13px; }
.acts { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
</style>
