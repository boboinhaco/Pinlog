<template>
  <!-- 기본 아치 사진: 나무 그늘 -->
  <svg viewBox="0 0 300 360" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient id="ar-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eaf2df" /><stop offset="1" stop-color="#c6d9b5" /></linearGradient>
      <filter id="ar-b"><feGaussianBlur stdDeviation="3" /></filter>
    </defs>
    <rect width="300" height="360" fill="url(#ar-sky)" />
    <g filter="url(#ar-b)">
      <circle cx="40" cy="60" r="70" fill="#6f9a5c" /><circle cx="150" cy="30" r="80" fill="#7fa96a" /><circle cx="265" cy="70" r="75" fill="#5f8a4f" />
      <circle cx="90" cy="150" r="60" fill="#8db577" /><circle cx="220" cy="170" r="65" fill="#6c9658" />
    </g>
    <path d="M150 360 C 148 290 140 230 150 180 C 158 140 185 120 210 110" stroke="#6b5842" stroke-width="12" fill="none" stroke-linecap="round" />
    <path d="M148 250 C 120 230 95 215 70 210" stroke="#6b5842" stroke-width="7" fill="none" stroke-linecap="round" />
    <g fill="#a8cc8e"><circle cx="70" cy="200" r="22" /><circle cx="215" cy="100" r="26" /><circle cx="120" cy="120" r="18" /></g>
    <g fill="#f3e7a8" opacity=".7"><circle cx="60" cy="40" r="4" /><circle cx="230" cy="50" r="5" /><circle cx="180" cy="200" r="3" /><circle cx="110" cy="90" r="3" /></g>
    <rect y="300" width="300" height="60" fill="#b9cf9f" />
  </svg>
</template>
