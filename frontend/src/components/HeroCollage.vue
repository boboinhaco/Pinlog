<template>
  <div class="collage" aria-hidden="true">
    <div class="p first"><SceneArt scene="coast" /><span class="overlay-l">좋아하는 걸,<br>더 가까운 일상으로</span></div>
    <div class="p"><SceneArt scene="houses" /></div>
    <div class="p hide-sm"><SceneArt scene="window" /></div>
    <div class="p text">
      <span>A MORE<br>BEAUTIFUL<br>TOMORROW</span>
      <small>with</small>
      <b>{{ BRAND }}</b>
    </div>
    <div class="p"><SceneArt scene="flowers" /></div>
    <div class="p hide-sm"><SceneArt scene="coffee" /></div>
    <div class="p note-p hide-sm"><div class="note-card">Collect<br>&nbsp;Plan<br>&nbsp;&nbsp;Go !</div></div>
    <div class="p last"><SceneArt scene="sea" /><span class="overlay">Places<br>&nbsp;Events<br>&nbsp;&nbsp;Memories<br>&nbsp;&nbsp;&nbsp;and More!</span></div>
  </div>
</template>

<script setup>
import { BRAND } from '../utils/brand'
import SceneArt from './SceneArt.vue'
</script>

<style scoped>
.collage { position: relative; display: grid; grid-template-columns: 1.3fr 1fr .95fr 1.15fr 1fr .6fr .8fr 1.35fr; height: 190px; background: #fbeef3; }
.p { position: relative; overflow: hidden; border-right: 3px solid #fff; }
.p:last-of-type { border-right: 0; }
.p :deep(svg) { width: 100%; height: 100%; display: block; }
.text { display: flex; flex-direction: column; justify-content: center; padding: 0 18px; background: var(--grad-soft); color: var(--hand-ink); }
.text span { font-family: var(--serif); font-size: 15px; letter-spacing: .14em; line-height: 1.45; }
.text small { font-family: var(--serif); font-style: italic; font-size: 11px; margin: 4px 0 -2px; }
.text b { font-family: var(--serif); font-size: 28px; font-weight: 600; font-style: italic; background: var(--cta); -webkit-background-clip: text; background-clip: text; color: transparent; }
.note-p { background: #fdeaf1; display: grid; place-items: center; }
.note-card { width: 76%; aspect-ratio: 4 / 5; padding: 14px 10px; background: #fffdfb; box-shadow: 0 6px 16px rgba(120, 30, 80, .15); transform: rotate(-8deg); font-family: var(--hand-en); font-size: 21px; line-height: 1.2; color: var(--hand-ink); }
.overlay-l { position: absolute; left: 18px; top: 22px; font-family: var(--hand-ko); font-size: 26px; line-height: 1.15; color: #fff; transform: rotate(-6deg); text-shadow: 0 1px 8px rgba(90, 20, 70, .45); }
.overlay { position: absolute; right: 16px; top: 70px; font-family: var(--hand-en); font-size: 22px; line-height: 1.08; color: #fff; transform: rotate(-8deg); text-shadow: 0 1px 8px rgba(90, 20, 70, .4); }
@media (max-width: 900px) {
  .collage { grid-template-columns: 1.2fr 1fr 1.2fr 1fr 1.2fr; height: 150px; }
  .hide-sm { display: none; }
}
@media (max-width: 520px) {
  .collage { grid-template-columns: 1fr 1.3fr 1fr; height: 120px; }
  .p:nth-child(2), .p:nth-child(5) { display: none; }
  .text b { font-size: 22px; }
  .text span { font-size: 12px; }
}
</style>
