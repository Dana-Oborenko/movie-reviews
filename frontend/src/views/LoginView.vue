<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')

async function submit() {
  localStorage.setItem('access_token', 'dev-token')
  localStorage.setItem('user_role', 'admin')
  localStorage.setItem('user_email', email.value || 'dev-admin@example.com')
  router.push('/admin')
}
</script>

<template>
  <div style="max-width:420px; margin:60px auto;">
    <h2 style="margin-bottom:16px;">Dev Login</h2>

    <div style="display:flex; flex-direction:column; gap:10px;">
      <input v-model="email" type="email" placeholder="Email" style="padding:10px;" />
      <input v-model="password" type="password" placeholder="Password" style="padding:10px;" />
      <button @click="submit" style="padding:10px; cursor:pointer;">
        Enter as Admin
      </button>
    </div>
  </div>
</template>