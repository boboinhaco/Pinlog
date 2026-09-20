<template>
  <!-- 홈 배너와 같은 사진을 얇은 띠로: 검토·내 일정·저장한 장소·좋아요 상단. 아래는 페이지 배경으로 흐려짐 -->
  <div class="band" aria-hidden="true">
    <img src="/home-bg.jpg" alt="" />
    <div class="shade"></div>
  </div>
</template>

<style scoped>
.band { position: relative; flex: none; width: 100%; aspect-ratio: 133 / 26; min-height: 170px; max-height: 300px; overflow: hidden; background: #f6e9ec; }
.band img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 44%; }
.shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(250, 250, 250, 0) 50%, var(--bg) 100%); }
@media (max-width: 760px) { .band { min-height: 150px; } .band img { object-position: 62% 44%; } }
</style>
