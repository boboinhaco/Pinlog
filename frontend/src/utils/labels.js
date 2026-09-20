// 화면 표시용 라벨 (카테고리·신뢰등급·필드 상태)
// 홈의 9개 블록 = 저장 카테고리 (백엔드 Category와 1:1)
export const CATEGORIES = [
  { key: 'POLICY_HOUSING', label: '청년 주거', desc: '월세 지원 · 임대주택 · 전세대출', tone: 'green' },
  { key: 'FINANCE', label: '금융상품', desc: '적금 · 청년계좌 · 예금', tone: 'yellow' },
  { key: 'EVENT', label: '축제·행사', desc: '페스티벌 · 전시 · 팝업', tone: 'pink' },
  { key: 'POLICY_JOB', label: '일자리', desc: '취업 지원 · 인턴 · 교육', tone: 'blue' },
  { key: 'POLICY_LIVING', label: '생활 지원', desc: '교통 · 문화 · 건강 지원금', tone: 'orange' },
  { key: 'SUBSCRIPTION', label: '주택 청약', desc: '청약 공고 · 특별공급', tone: 'brown' },
  { key: 'RECRUIT', label: '모집', desc: '서포터즈 · 대외활동 · 체험단', tone: 'purple' },
  { key: 'CONTEST', label: '공모전', desc: '아이디어 · 디자인 · 영상', tone: 'red' },
  { key: 'OTHER', label: '기타', desc: '분류하기 애매한 것들', tone: 'gray' }
]
// 지도 핀·범례 색 (카테고리 tone 기준)
const PIN = { green: '#3f9a6b', yellow: '#d4a22a', pink: '#d9578a', blue: '#4a72d8', orange: '#e07b2e', brown: '#9a6f55', purple: '#7c5cc4', red: '#d24a4a', gray: '#6b7489' }
export const pinColor = key => PIN[CATEGORIES.find(c => c.key === key)?.tone] ?? PIN.gray
export const CATEGORY = Object.fromEntries(CATEGORIES.map(c => [c.key, c]))
export const CATEGORY_LABEL = Object.fromEntries(CATEGORIES.map(c => [c.key, c.label]))
export const GRADE = {
  HIGH: { label: '공식 근거 확인', tone: 'green' },
  REVIEW: { label: '확인 필요', tone: 'orange' },
  UNVERIFIED: { label: '공식 미확인', tone: 'gray' }
}
export const STATUS = {
  VERIFIED: { label: '일치', tone: 'green' },
  REFINED: { label: '공식이 더 자세함', tone: 'blue' },
  CONFLICT: { label: '내용이 달라요', tone: 'red' },
  ADDED: { label: '공식에만 있음', tone: 'purple' },
  AMBIGUOUS: { label: '확인 필요', tone: 'orange' },
  UNVERIFIED: { label: '공식 미확인', tone: 'gray' }
}
// 비교표 행 순서
export const FIELD_LABEL = {
  title: '무엇인지', target: '대상', eligibility: '자격요건', apply_period: '신청 기간 · 마감', event_period: '행사 기간',
  benefit_amount: '혜택', location: '장소', requirements: '준비 서류'
}

// 추출값(문자열·배열·객체)을 한 줄 문장으로
export const display = v => {
  if (v == null || v === '' || (Array.isArray(v) && !v.length)) return null
  if (Array.isArray(v)) return v.join(', ')
  if (typeof v === 'object') {
    if (v.text) return v.text
    if ('start' in v || 'end' in v) return [v.start, v.end].filter(Boolean).join(' ~ ') || null
    if (v.name) return [v.name, v.address].filter(Boolean).join(' · ')
    return null
  }
  return String(v)
}

// 검증 필드 + 추출값으로 비교 행 구성 (검증에 없는 추출 항목은 '공식 미확인')
export const compareRows = (extraction, fields = []) => {
  const byField = Object.fromEntries(fields.map(f => [f.field, f]))
  return Object.keys(FIELD_LABEL).map(key => {
    const f = byField[key], sns = display(f?.sns_value) ?? display(extraction?.[key])
    if (!f && !sns) return null
    return { key, label: FIELD_LABEL[key], sns, official: display(f?.official_value), status: f?.status ?? 'UNVERIFIED', evidence: f?.evidence }
  }).filter(Boolean)
}
