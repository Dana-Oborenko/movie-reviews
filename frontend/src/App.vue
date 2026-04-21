<script setup>
// App shell: layout + theme switcher + RouterView + Logout + current user (email/role)
import { RouterView, useRouter, useRoute } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import { supabase } from './supabase'
import { api } from './api'

const router = useRouter()
const route = useRoute()

const isAdminPage = computed(() => route.path.startsWith('/admin'))
const isLoginPage = computed(() => route.path === '/login')
const headerTitle = computed(() => (isAdminPage.value ? 'Movie Reviews — Admin' : 'Movie Reviews'))

// theme: 'light' | 'dark' | 'system'
const theme = ref('system')

// current user info from backend (/me)
const currentUser = ref(null)

function applyTheme(value) {
  // Attach theme to <html data-theme="...">
  const root = document.documentElement
  root.dataset.theme = value
}

async function loadMe() {
  try {
    const { data } = await api.get('/me')
    currentUser.value = data
    localStorage.setItem('user_role', data.role || 'user')
    localStorage.setItem('user_email', data.email || '')
  } catch (e) {
    currentUser.value = null
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_email')
  }
}

function logout() {
  // Supabase logout + local token cleanup
  supabase.auth.signOut()
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_email')
  currentUser.value = null
  router.push('/login')
}

onMounted(async () => {
  // Load saved theme from localStorage
  const saved = localStorage.getItem('theme')
  if (saved === 'light' || saved === 'dark' || saved === 'system') {
    theme.value = saved
  }
  applyTheme(theme.value)

  // Load current user (role/email) for header
  await loadMe()
})

// React to manual theme changes
watch(theme, (value) => {
  localStorage.setItem('theme', value)
  applyTheme(value)
})
</script>

<template>
  <main style="padding:24px; max-width:960px; margin:0 auto; font-family:system-ui">
    <header
      :style="{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: isLoginPage ? '32px' : '16px'
      }"
    >
      <div class="brandBlock">
        <h1 class="brandTitle">{{ headerTitle }}</h1>
        <p class="brandSubtitle">
          Discover films, share impressions, and explore sentiment analysis.
        </p>
      </div>

      <div style="display:flex; align-items:center; gap:12px;">
        <!-- user badge -->
        <span v-if="currentUser && isAdminPage" style="opacity:0.85">
          {{ currentUser.email }} ({{ currentUser.role }})
        </span>

        <!-- theme switcher -->
        <div style="display:flex; align-items:center; gap:8px;">
          <label for="theme-select">Theme:</label>
          <select id="theme-select" v-model="theme" style="padding:4px 6px;">
            <option value="system">System</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <!-- logout -->
        <button
          v-if="isAdminPage"
          @click="logout"
          style="padding:6px 10px; cursor:pointer"
        >
          Logout
        </button>
      </div>
    </header>

    <RouterView />
  </main>
</template>

<style>
:root {
  --bg-light: #ffffff;
  --text-light: #111111;
  --bg-dark: #111111;
  --text-dark: #f5f5f5;
}

body {
  margin: 0;
  background: var(--bg-light);
  color: var(--text-light);
}

:root[data-theme='light'] body {
  background: var(--bg-light);
  color: var(--text-light);
}

:root[data-theme='dark'] body {
  background: var(--bg-dark);
  color: var(--text-dark);
}

@media (prefers-color-scheme: dark) {
  :root[data-theme='system'] body {
    background: var(--bg-dark);
    color: var(--text-dark);
  }
}
@media (prefers-color-scheme: light) {
  :root[data-theme='system'] body {
    background: var(--bg-light);
    color: var(--text-light);
  }
}

.brandBlock {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brandTitle {
  margin: 0;
  font-size: 2.2rem;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brandSubtitle {
  margin: 0;
  font-size: 0.95rem;
  opacity: 0.7;
}
</style>
