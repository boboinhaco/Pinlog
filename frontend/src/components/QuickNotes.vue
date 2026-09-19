<template>
  <section class="notes">
    <h3 class="section-title">The quick notes</h3>
    <ul>
      <li v-for="(n, i) in notes" :key="i" :class="{ done: n.done }">
        <input v-model="n.done" type="checkbox" :aria-label="n.text" @change="save" />
        <input v-model="n.text" class="txt" placeholder="할 일" @blur="save" @keydown.enter.prevent="$event.target.blur()" />
        <button class="text del" aria-label="삭제" @click="notes.splice(i, 1); save()">×</button>
      </li>
    </ul>
    <form class="add" @submit.prevent="add">
      <input v-model="draft" placeholder="+ To-do 추가" aria-label="할 일 추가" />
    </form>
    <p v-if="error" class="err">{{ error }}</p>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

// 체크리스트 메모, 계정에 저장
const auth = useAuthStore()
const notes = ref([]), draft = ref(''), error = ref('')
watch(() => auth.user?.notes, v => { notes.value = (v ?? []).map(n => ({ ...n })) }, { immediate: true })

async function save() {
  error.value = ''
  try { await auth.update({ notes: notes.value.filter(n => n.text.trim()) }) } catch (e) { error.value = e.message }
}
function add() {
  if (!draft.value.trim()) return
  notes.value.push({ text: draft.value.trim(), done: false }); draft.value = ''; save()
}
</script>

<style scoped>
.notes { border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }
.section-title { font-size: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }
ul { list-style: none; margin: 0; padding: 0; }
li { display: flex; align-items: center; gap: 8px; }
li input[type=checkbox] { width: 16px; height: 16px; flex: none; accent-color: var(--blue); }
.txt { border: 0; padding: 4px 2px; font-size: 14px; }
.txt:focus { outline: none; background: var(--soft); }
li.done .txt { color: var(--faint); text-decoration: line-through; }
.del { opacity: 0; font-size: 16px; }
li:hover .del, .del:focus { opacity: 1; }
.add input { margin-top: 6px; border: 0; padding: 4px 2px; font-size: 14px; color: var(--muted); }
.add input:focus { outline: none; background: var(--soft); }
.err { margin: 6px 0 0; color: var(--i-red); font-size: 13px; }
@media (hover: none) { .del { opacity: 1; } }
</style>
