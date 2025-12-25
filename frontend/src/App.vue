<script setup>
// App shell: layout + theme switcher + RouterView
import { RouterView } from 'vue-router'
import { ref, onMounted, watch } from 'vue'

// theme: 'light' | 'dark' | 'system'
const theme = ref('system')

function applyTheme(value) {
  // Attach theme to <html data-theme="...">
  const root = document.documentElement
  root.dataset.theme = value
}

onMounted(() => {
  // Load saved theme from localStorage
  const saved = localStorage.getItem('theme')
  if (saved === 'light' || saved === 'dark' || saved === 'system') {
    theme.value = saved
  }

  applyTheme(theme.value)
})

// React to manual theme changes
watch(theme, (value) => {
  localStorage.setItem('theme', value)
  applyTheme(value)
})
</script>

<template>
  <main style="padding:24px; max-width:960px; margin:0 auto; font-family:system-ui">
    <!-- Header with title + theme switcher -->
    <header
      style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;"
    >
      <h1 style="margin:0;">Movie Reviews — Admin</h1>

      <div style="display:flex; align-items:center; gap:8px;">
        <label for="theme-select">Theme:</label>
        <select
          id="theme-select"
          v-model="theme"
          style="padding:4px 6px;"
        >
          <option value="system">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
    </header>

    <!-- Page content -->
    <RouterView />
  </main>
</template>


<style>
/* Theme color variables */
:root {
  --bg-light: #ffffff;
  --text-light: #111111;
  --bg-dark: #111111;
  --text-dark: #f5f5f5;
}

/* Base styles (default light) */
body {
  margin: 0;
  background: var(--bg-light);
  color: var(--text-light);
}

/* Explicit light theme */
:root[data-theme='light'] body {
  background: var(--bg-light);
  color: var(--text-light);
}

/* Explicit dark theme */
:root[data-theme='dark'] body {
  background: var(--bg-dark);
  color: var(--text-dark);
}

/* System theme: follow OS preference */
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
</style>

