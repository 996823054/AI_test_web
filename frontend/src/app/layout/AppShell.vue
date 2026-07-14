<template>
  <div class="app-shell">
    <header class="site-header">
      <div class="sidebar-brand">
        <strong>AI 测试平台</strong>
        <span>Testing Asset Platform</span>
      </div>
      <nav class="top-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="sidebar-link"
          :class="{ active: route.path.startsWith(item.to) }"
        >
          {{ item.label }}
          <small>{{ item.desc }}</small>
        </RouterLink>
      </nav>
    </header>
    <div class="main-area">
      <header class="topbar">
        <div class="breadcrumb">
          <strong>{{ currentTitle }}</strong>
        </div>
      </header>
      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { navGroups } from '../navigation.js'

const route = useRoute()

const navItems = computed(() => navGroups.flatMap((group) => group.items))

const currentTitle = computed(() => {
  for (const group of navGroups) {
    const match = group.items.find((item) => route.path.startsWith(item.to))
    if (match) return match.label
  }
  return 'AI 测试平台'
})
</script>
