<template>
  <div class="cmp">
    <div class="cmp-head"><span>항목</span><span>SNS 링크에서</span><span>공식 공고에서</span><span>확인 결과</span></div>
    <div v-for="r in rows" :key="r.key" class="cmp-row" :class="r.status">
      <span class="k">{{ r.label }}</span>
      <span class="v"><i class="m">SNS</i>{{ r.sns ?? '언급 없음' }}</span>
      <span class="v official"><i class="m">공식</i>{{ r.official ?? (r.status === 'UNVERIFIED' ? '찾지 못함' : '-') }}
        <q v-if="r.evidence">{{ r.evidence }}</q>
      </span>
      <span><b class="tag" :class="`tone-${STATUS[r.status].tone}`">{{ STATUS[r.status].label }}</b></span>
    </div>
  </div>
</template>

<script setup>
import { STATUS } from '../utils/labels'
defineProps({ rows: { type: Array, required: true } })
</script>

<style scoped>
.cmp { font-size: 14px; }
.cmp-head, .cmp-row { display: grid; grid-template-columns: 120px 1fr 1.2fr 128px; gap: 16px; padding: 14px 4px; align-items: start; }
.cmp-head { font-size: 13px; color: var(--muted); border-bottom: 1px solid var(--line); padding-top: 0; }
.cmp-row { border-bottom: 1px solid var(--line); }
.cmp-row:last-child { border-bottom: 0; }
.cmp-row.CONFLICT { background: #fdf5f5; margin: 0 -10px; padding-inline: 14px; border-radius: 6px; }
.k { font-weight: 700; }
.v { line-height: 1.5; word-break: keep-all; }
.official { color: var(--ink); }
.m { display: none; font-style: normal; font-size: 11px; font-weight: 700; color: var(--muted); margin-right: 6px; }
q { display: block; margin-top: 6px; padding-left: 10px; border-left: 3px solid var(--line-strong); font-size: 12.5px; color: #7b7480; quotes: none; }
.tag { font-weight: 500; }
@media (max-width: 760px) {
  .cmp-head { display: none; }
  .cmp-row { grid-template-columns: 1fr auto; gap: 6px 10px; }
  .k { grid-column: 1; }
  .cmp-row > span:last-child { grid-column: 2; grid-row: 1; }
  .v { grid-column: 1 / -1; }
  .m { display: inline; }
}
</style>
