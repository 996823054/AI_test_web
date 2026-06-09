<template>
  <div>
    <PageHeader
      title="首页 / 质量驾驶舱"
      subtitle="查看平台健康状态、资产概览，并快速进入需求中心、Case 中心与系统设置。"
    />

    <section class="metric-grid">
      <article class="metric-card">
        <div class="label">服务状态</div>
        <div class="value">{{ serviceStatus }}</div>
        <div class="hint">{{ platformName }}</div>
      </article>
      <article class="metric-card">
        <div class="label">数据库</div>
        <div class="value">{{ databaseStatus }}</div>
        <div class="hint">后端健康检查</div>
      </article>
      <article class="metric-card">
        <div class="label">需求文档</div>
        <div class="value">{{ documentTotal }}</div>
        <div class="hint">需求中心资产</div>
      </article>
      <article class="metric-card">
        <div class="label">Case 资产</div>
        <div class="value">{{ caseTotal }}</div>
        <div class="hint">Case 中心正式资产</div>
      </article>
    </section>

    <section class="panel-card">
      <div class="panel-card-header">模块快捷入口</div>
      <div class="panel-card-body">
        <div class="quick-links">
          <RouterLink to="/requirements" class="quick-link-card">
            <strong>需求中心</strong>
            <span>进入需求资产工作台，查看文档库、原文预览与入库门禁。</span>
          </RouterLink>
          <RouterLink to="/cases" class="quick-link-card">
            <strong>Case 中心</strong>
            <span>进入 Case 资产工作台，查看正式 case、来源追溯与覆盖信息。</span>
          </RouterLink>
          <RouterLink to="/settings" class="quick-link-card">
            <strong>系统设置</strong>
            <span>管理 AI 模型、脱敏规则与报告保留策略。</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../shared/components/PageHeader.vue'
import { fetchOverviewStats } from '../api.js'

const health = ref(null)
const documentTotal = ref('—')
const caseTotal = ref('—')

const serviceStatus = computed(() => health.value?.data?.service?.status || '—')
const databaseStatus = computed(() => health.value?.data?.database?.status || '—')
const platformName = computed(() => health.value?.data?.service?.name || 'AI 测试平台')

onMounted(async () => {
  try {
    const stats = await fetchOverviewStats()
    health.value = stats.health
    documentTotal.value = stats.documentTotal
    caseTotal.value = stats.caseTotal
  } catch {
    health.value = null
  }
})
</script>
