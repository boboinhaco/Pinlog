<template>
  <!-- 기본 커버: 흐릿한 잎사귀 (사용자 사진으로 교체 가능) -->
  <svg viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient id="cv-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfdcc6" /><stop offset=".55" stop-color="#8fae86" /><stop offset="1" stop-color="#e8d6c4" /></linearGradient>
      <linearGradient id="cv-leaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6f9a62" /><stop offset="1" stop-color="#3f6a3b" /></linearGradient>
      <linearGradient id="cv-leaf2" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#a9c79a" /><stop offset="1" stop-color="#e3edd6" /></linearGradient>
      <filter id="cv-b1"><feGaussianBlur stdDeviation="14" /></filter>
      <filter id="cv-b2"><feGaussianBlur stdDeviation="5" /></filter>
    </defs>
    <rect width="1200" height="300" fill="url(#cv-bg)" />
    <g filter="url(#cv-b1)" opacity=".9">
      <ellipse cx="160" cy="80" rx="260" ry="120" fill="#4e7a45" transform="rotate(-18 160 80)" />
      <ellipse cx="620" cy="-10" rx="300" ry="110" fill="#5d8a52" transform="rotate(8 620 -10)" />
      <ellipse cx="1060" cy="250" rx="240" ry="90" fill="#f0e1cf" />
    </g>
    <g filter="url(#cv-b2)">
      <path d="M760 300 C 770 190 860 110 1010 90 C 960 190 880 270 760 300 Z" fill="url(#cv-leaf2)" opacity=".9" />
      <path d="M840 300 C 880 220 980 170 1120 170 C 1060 240 960 290 840 300 Z" fill="url(#cv-leaf)" opacity=".75" />
      <path d="M300 300 C 320 230 400 190 500 190 C 470 250 400 290 300 300 Z" fill="url(#cv-leaf2)" opacity=".7" />
      <path d="M1000 0 C 990 60 1040 120 1130 130 C 1140 80 1090 20 1000 0 Z" fill="#c9dcb9" opacity=".8" />
    </g>
  </svg>
</template>
