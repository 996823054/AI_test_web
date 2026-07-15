<template>
  <section class="module-page">
    <PageHeader :title="title" :subtitle="description" />
    <EmptyState v-if="!loading && !error && items.length === 0" title="暂无数据" description="模块骨架已接入，等待后端资产填充。" />
    <p v-if="error" class="error">{{ error }}</p>
    <LogPanel v-if="logs.length" :lines="logs" />
    <StepTimeline v-if="steps.length" :steps="steps" />
    <EvidenceViewer v-if="evidence" :evidence="evidence" />
    <ul v-if="items.length" class="item-list">
      <li v-for="(item, index) in items" :key="index">{{ formatItem(item) }}</li>
    </ul>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '../../../shared/components/PageHeader.vue'
import EmptyState from '../../../shared/components/EmptyState.vue'
import EvidenceViewer from '../../../shared/components/EvidenceViewer.vue'
import StepTimeline from '../../../shared/components/StepTimeline.vue'
import LogPanel from '../../../shared/components/LogPanel.vue'
import { fetchDashboard as loadData } from '../api'

const title = '报告中心'
const description = '报告、证据与导出'
const loading = ref(true)
const error = ref('')
const items = ref([])
const logs = ref([])
const steps = ref([])
const evidence = ref(null)

function formatItem(item) {
  if (typeof item === 'string') return item
  return item.name || item.title || item.id || JSON.stringify(item)
}

onMounted(async () => {
  try {
    const data = await loadData()
    if (Array.isArray(data)) items.value = data
    else if (Array.isArray(data?.items)) items.value = data.items
    else if (data) items.value = [data]
    logs.value = ['module:loaded', `module:reports`]
    steps.value = [{ name: '加载模块数据', status: 'passed' }]
    evidence.value = { module: 'reports', sample: items.value[0] || null }
  } catch (err) {
    error.value = err.message || String(err)
    logs.value = ['module:load_failed', error.value]
    steps.value = [{ name: '加载模块数据', status: 'failed' }]
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.module-page { display: grid; gap: 16px; }
.error { color: #b42318; }
.item-list { margin: 0; padding-left: 18px; }
</style>
