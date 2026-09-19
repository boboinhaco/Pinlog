<template>
  <form class="auth" @submit.prevent="submit">
    <input v-if="mode === 'signup'" v-model="name" placeholder="이름 (선택)" autocomplete="name" />
    <input v-model="email" type="email" placeholder="이메일" autocomplete="email" required />
    <input v-model="password" type="password" :placeholder="mode === 'signup' ? '비밀번호 (8자 이상)' : '비밀번호'"
           :autocomplete="mode === 'signup' ? 'new-password' : 'current-password'" required :minlength="mode === 'signup' ? 8 : undefined" />
    <button :disabled="busy">{{ busy ? '잠시만요…' : mode === 'signup' ? '가입하기' : '로그인' }}</button>
    <p v-if="error" class="err" role="alert">{{ error }}</p>
    <button type="button" class="text switch" @click="mode = mode === 'signup' ? 'login' : 'signup'; error = ''">
      {{ mode === 'signup' ? '이미 계정이 있어요 · 로그인' : '처음이에요 · 회원가입' }}
    </button>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

// 로그인/회원가입 폼 (성공 시 done 이벤트)
const props = defineProps({ initialMode: { type: String, default: 'login' } })
const emit = defineEmits(['done', 'mode'])
const auth = useAuthStore()
const mode = ref(props.initialMode), name = ref(''), email = ref(''), password = ref(''), busy = ref(false), error = ref('')
watch(mode, m => emit('mode', m), { immediate: true })

async function submit() {
  busy.value = true; error.value = ''
  try {
    if (mode.value === 'signup') await auth.signup(email.value, password.value, name.value)
    else await auth.login(email.value, password.value)
    password.value = ''
    emit('done')
  } catch (e) { error.value = e.message } finally { busy.value = false }
}
</script>

<style scoped>
.auth { display: grid; gap: 8px; }
.switch { justify-self: start; font-size: 13px; }
.err { margin: 0; color: var(--i-red); font-size: 13px; }
</style>
