<template>
  <div>
    <PageHeader
      title="系统设置"
      subtitle="统一管理 AI 模型、脱敏规则与报告策略。密钥仅允许写入，前端只展示 api_key_masked。"
    >
      <template #actions>
        <button type="button" class="btn" @click="confirmReset">恢复默认</button>
        <button type="button" class="btn primary" @click="saveCurrentTab">保存当前配置</button>
      </template>
    </PageHeader>

    <div v-if="message" class="message" :class="messageTone">{{ message }}</div>

    <div class="tabs">
      <button type="button" class="tab" :class="{ active: activeTab === 'models' }" @click="activeTab = 'models'">
        AI 模型
      </button>
      <button type="button" class="tab" :class="{ active: activeTab === 'security' }" @click="activeTab = 'security'">
        安全脱敏
      </button>
      <button type="button" class="tab" :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">
        报告策略
      </button>
      <button type="button" class="tab" :class="{ active: activeTab === 'future' }" @click="activeTab = 'future'">
        环境 / Appium
      </button>
    </div>

    <section v-if="activeTab === 'models'" class="panel-card">
      <div class="panel-card-header">AI 模型配置</div>
      <div class="panel-card-body">
        <div class="toolbar">
          <button type="button" class="btn primary" @click="openModelEditor()">新增模型</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>模型</th>
              <th>Provider</th>
              <th>状态</th>
              <th>Key</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in aiModels" :key="item.id">
              <td>
                <strong>{{ item.name }}</strong>
                <div class="list-item-meta">{{ item.model }}</div>
              </td>
              <td>{{ item.provider }}</td>
              <td>
                <StatusBadge :label="item.connection_status || 'unchecked'" :tone="statusTone(item.connection_status)" />
                <div class="list-item-meta">{{ item.is_default ? '默认模型' : '—' }}</div>
              </td>
              <td>{{ item.api_key_masked || '—' }}</td>
              <td>
                <div class="toolbar">
                  <button type="button" class="btn" @click="openModelEditor(item)">编辑</button>
                  <button type="button" class="btn" @click="runCheck(item.id)">检测</button>
                  <button type="button" class="btn" :disabled="item.is_default" @click="makeDefault(item.id)">设默认</button>
                  <button type="button" class="btn danger" :disabled="item.is_default" @click="removeModel(item.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-if="!aiModels.length" title="暂无模型配置" description="新增模型后需通过连接检测，才能设为默认模型。" />
      </div>
    </section>

    <section v-else-if="activeTab === 'security'" class="panel-card">
      <div class="panel-card-header">安全脱敏</div>
      <div class="panel-card-body">
        <div class="field">
          <label>脱敏开关</label>
          <select v-model="settings.security.masking_enabled" class="select">
            <option :value="true">启用</option>
            <option :value="false">关闭</option>
          </select>
        </div>
        <div class="field">
          <label>审计开关</label>
          <select v-model="settings.security.audit_enabled" class="select">
            <option :value="true">启用</option>
            <option :value="false">关闭</option>
          </select>
        </div>
        <div class="field">
          <label>脱敏字段规则</label>
          <textarea v-model="maskFieldsText" class="textarea" placeholder="Authorization, Cookie, token, password..." />
        </div>
        <p class="list-item-meta">API Key 不允许明文返回，前端仅展示 api_key_masked。</p>
      </div>
    </section>

    <section v-else-if="activeTab === 'report'" class="panel-card">
      <div class="panel-card-header">报告策略</div>
      <div class="panel-card-body">
        <div class="field">
          <label>报告保留天数</label>
          <input v-model.number="settings.report.retention_days" class="input" type="number" min="1" />
        </div>
        <div class="field">
          <label>产物保留天数</label>
          <input v-model.number="settings.report.artifact_retention_days" class="input" type="number" min="1" />
        </div>
        <div class="field">
          <label>导出脱敏</label>
          <select v-model="settings.report.export_masking" class="select">
            <option :value="true">启用</option>
            <option :value="false">关闭</option>
          </select>
        </div>
      </div>
    </section>

    <section v-else class="panel-card">
      <div class="panel-card-header">环境 / Appium（后续启用）</div>
      <div class="panel-card-body">
        <EmptyState title="后续切片启用" description="环境变量、Appium capability 模板将在移动端与执行中心切片完成后开放。" />
      </div>
    </section>

    <div v-if="modelEditorVisible" class="modal-backdrop" @click.self="modelEditorVisible = false">
      <div class="modal">
        <h3>{{ modelForm.id ? '编辑模型' : '新增模型' }}</h3>
        <div class="field">
          <label>名称</label>
          <input v-model="modelForm.name" class="input" />
        </div>
        <div class="field">
          <label>Provider</label>
          <input v-model="modelForm.provider" class="input" />
        </div>
        <div class="field">
          <label>Model</label>
          <input v-model="modelForm.model" class="input" />
        </div>
        <div class="field">
          <label>API Key</label>
          <input v-model="modelForm.api_key" class="input" placeholder="留空表示保留已有密钥" />
        </div>
        <div class="field">
          <label>Base URL</label>
          <input v-model="modelForm.base_url" class="input" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="modelEditorVisible = false">取消</button>
          <button type="button" class="btn primary" @click="submitModel">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '../../../shared/components/PageHeader.vue'
import StatusBadge from '../../../shared/components/StatusBadge.vue'
import EmptyState from '../../../shared/components/EmptyState.vue'
import {
  checkAiModel,
  deleteAiModel,
  fetchAiModels,
  fetchSettings,
  resetSettings,
  saveAiModel,
  saveSettings,
  setDefaultAiModel,
} from '../api.js'

const activeTab = ref('models')
const message = ref('')
const messageTone = ref('info')
const aiModels = ref([])
const modelEditorVisible = ref(false)
const settings = reactive({
  security: { masking_enabled: true, audit_enabled: true, mask_fields: [] },
  report: { retention_days: 14, artifact_retention_days: 14, export_masking: true },
})
const modelForm = reactive({
  id: '',
  name: '',
  provider: 'openai',
  model: 'gpt-4',
  api_key: '',
  base_url: '',
})

const maskFieldsText = computed({
  get() {
    return (settings.security.mask_fields || []).join(', ')
  },
  set(value) {
    settings.security.mask_fields = value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
  },
})

function showMessage(text, tone = 'info') {
  message.value = text
  messageTone.value = tone
}

function statusTone(status) {
  if (status === 'passed') return 'success'
  if (status === 'failed') return 'danger'
  return 'neutral'
}

async function loadAll() {
  try {
    const [settingsResponse, modelsResponse] = await Promise.all([
      fetchSettings(),
      fetchAiModels(),
    ])
    Object.assign(settings.security, settingsResponse.security || {})
    Object.assign(settings.report, settingsResponse.report || {})
    aiModels.value = modelsResponse.items || []
  } catch (error) {
    showMessage(`加载系统设置失败：${error.message}`, 'danger')
  }
}

function openModelEditor(item = null) {
  modelForm.id = item?.id || ''
  modelForm.name = item?.name || ''
  modelForm.provider = item?.provider || 'openai'
  modelForm.model = item?.model || 'gpt-4'
  modelForm.api_key = ''
  modelForm.base_url = item?.base_url || ''
  modelEditorVisible.value = true
}

async function submitModel() {
  try {
    const payload = {
      id: modelForm.id || undefined,
      name: modelForm.name,
      provider: modelForm.provider,
      model: modelForm.model,
      base_url: modelForm.base_url,
    }
    if (modelForm.api_key) payload.api_key = modelForm.api_key
    await saveAiModel(payload)
    modelEditorVisible.value = false
    showMessage('模型保存成功', 'success')
    await loadAll()
  } catch (error) {
    showMessage(`保存模型失败：${error.message}`, 'danger')
  }
}

async function runCheck(modelId) {
  try {
    const result = await checkAiModel(modelId)
    showMessage(result.message || '连接检测完成', result.success === false ? 'danger' : 'success')
    await loadAll()
  } catch (error) {
    showMessage(`连接检测失败：${error.message}`, 'danger')
  }
}

async function makeDefault(modelId) {
  try {
    await setDefaultAiModel(modelId)
    showMessage('默认模型已更新', 'success')
    await loadAll()
  } catch (error) {
    showMessage(`设置默认模型失败：${error.message}`, 'danger')
  }
}

async function removeModel(modelId) {
  if (!window.confirm('确认删除该模型配置？')) return
  try {
    await deleteAiModel(modelId)
    showMessage('模型已删除', 'success')
    await loadAll()
  } catch (error) {
    showMessage(`删除模型失败：${error.message}`, 'danger')
  }
}

async function saveCurrentTab() {
  try {
    if (activeTab.value === 'models') {
      showMessage('模型配置通过独立保存/检测流程维护', 'info')
      return
    }
    await saveSettings({
      security: settings.security,
      report: settings.report,
    })
    showMessage('系统设置保存成功', 'success')
    await loadAll()
  } catch (error) {
    showMessage(`保存失败：${error.message}`, 'danger')
  }
}

async function confirmReset() {
  if (!window.confirm('确认恢复默认系统设置？')) return
  try {
    await resetSettings()
    showMessage('已恢复默认设置', 'success')
    await loadAll()
  } catch (error) {
    showMessage(`恢复默认失败：${error.message}`, 'danger')
  }
}

onMounted(loadAll)
</script>
