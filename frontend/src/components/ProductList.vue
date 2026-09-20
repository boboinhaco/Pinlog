<template>
  <!-- 사진·글에서 찾은 상품 목록: 검토 화면은 체크박스로 고르고(selectable), 상세 화면은 보기만 -->
  <div>
    <component :is="selectable ? 'label' : 'div'" v-for="(p, i) in products" :key="p.name + i" class="pd" :class="{ pick: selectable, off: selectable && !p.on }">
      <input v-if="selectable" type="checkbox" :checked="p.on" @change="emit('toggle', i)" />
      <span class="body">
        <span class="top"><b>{{ p.matched_name || p.name }}</b><span class="tag" :class="`tone-${PRODUCT_CONF[p.confidence]?.tone ?? 'gray'}`">{{ PRODUCT_CONF[p.confidence]?.label ?? '확인 필요' }}</span></span>
        <small class="sub">{{ sub(p) }}</small>
        <small v-if="p.note" class="note">{{ p.note }}</small>
        <span class="links"><a v-for="l in p.links" :key="l.url" :href="l.url" target="_blank" rel="noopener" :class="l.kind" @click.stop>{{ LINK_KIND[l.kind] ?? '참고' }} · {{ host(l.url) }} ↗</a></span>
      </span>
    </component>
  </div>
</template>

<script setup>
import { PRODUCT_CONF, LINK_KIND } from '../utils/labels'
import { host } from '../utils/source'

defineProps({ products: { type: Array, required: true }, selectable: Boolean })
const emit = defineEmits(['toggle'])
// 게시물 표현 · 브랜드 · 종류 · 특징 · 게시물 가격
const sub = p => [p.matched_name && p.matched_name !== p.name ? `게시물 표현: ${p.name}` : null, p.brand, p.kind, p.features, p.price_text && `게시물 가격 ${p.price_text}`].filter(Boolean).join(' · ')
</script>

<style scoped>
.pd { display: grid; gap: 4px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.pd:last-child { border-bottom: 0; padding-bottom: 2px; }
.pd.pick { grid-template-columns: auto 1fr; gap: 10px; align-items: start; cursor: pointer; }
.pd.off { opacity: .45; }
.pd input { width: 18px; height: 18px; margin-top: 2px; accent-color: var(--accent); }
.body { display: grid; gap: 4px; min-width: 0; }
.top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.top b { font-size: 14.5px; }
.sub { font-size: 12.5px; color: var(--muted); }
.note { font-size: 12.5px; color: #8a4a12; }
.links { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
.links a { padding: 3px 10px; border-radius: 999px; border: 1px solid var(--line-strong); background: #fff; font-size: 12px; text-decoration: none; color: var(--ink); }
.links a.official { border-color: var(--accent); color: var(--accent); font-weight: 600; }
.links a.shop { color: var(--accent-deep); }
.links a.search { color: var(--muted); }
.links a:hover { background: var(--hover); }
</style>
