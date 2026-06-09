<template>
  <div>
    <PageHeader
      title="Case 资产工作台"
      subtitle="Case 中心统一管理正式 case 资产。AI 确认后的 case 进入可信资产边界，需保留来源追溯与人工确认记录。"
    >
      <template #actions>
        <button type="button" class="btn primary" @click="openCreate">新建 Case</button>
      </template>
    </PageHeader>

    <div v-if="message" class="message" :class="messageTone">{{ message }}</div>

    <section class="workspace-layout">
      <aside class="panel-card">
        <div class="panel-card-header">可信资产边界</div>
        <div class="panel-card-body">
          <p class="list-item-meta">仅展示已启用、来源可追溯的正式 case 资产。</p>
          <div class="metric-card" style="margin-top: 12px;">
            <div class="label">资产总数</div>
            <div class="value">{{ total }}</div>
          </div>
          <div class="toolbar" style="margin-top: 16px;">
            <input v-model="filters.keyword" class="input" placeholder="名称或描述" @keyup.enter="loadCases" />
            <select v-model="filters.case_kind" class="select">
              <option value="">全部类型</option>
              <option value="api">接口 case</option>
              <option value="functional">功能 case</option>
              <option value="automation">自动化 case</option>
              <option value="mobile">移动端 case</option>
              <option value="scenario">场景 / 编排 case</option>
            </select>
            <select v-model="filters.source" class="select">
              <option value="">全部来源</option>
              <option value="manual">manual</option>
              <option value="ai_generated">ai_generated</option>
            </select>
            <select v-model="filters.lifecycle_status" class="select" @change="loadCases">
              <option value="active">活跃资产</option>
              <option value="deprecated">已废弃治理视图</option>
              <option value="">全部生命周期</option>
            </select>
            <select v-model="filters.importance" class="select" @change="loadCases">
              <option value="">全部重要性</option>
              <option value="high">高重要性</option>
              <option value="normal">普通</option>
            </select>
            <label class="list-item-meta">
              <input v-model="filters.module_delivery" type="checkbox" @change="loadCases" />
              模块完整交付
            </label>
            <button type="button" class="btn" @click="loadCases">查询</button>
          </div>
          <div class="panel-card-header" style="margin-top: 16px;">AI 草稿待处理（{{ drafts.length }}）</div>
          <div
            v-for="draft in drafts"
            :key="draft.id"
            class="list-item"
            :class="{ selected: selectedDraftId === draft.id }"
            @click="selectDraft(draft.id)"
          >
            <div class="list-item-title">{{ draft.name }}</div>
            <div class="list-item-meta">{{ draft.case_kind }} · {{ draft.status }}</div>
            <div v-if="draft.reject_reason" class="list-item-meta">门禁原因：{{ draft.reject_reason }}</div>
          </div>
          <div v-if="!drafts.length" class="list-item-meta">暂无待确认草稿</div>
        </div>
      </aside>

      <section class="panel-card">
        <div class="panel-card-header">正式 case 列表</div>
        <div class="panel-card-body">
          <div v-if="loading" class="empty-state">加载中...</div>
          <div
            v-for="item in cases"
            :key="item.id"
            class="list-item"
            :class="{ selected: selectedId === item.id }"
            @click="selectCase(item.id)"
          >
            <div class="list-item-title">{{ item.name }}</div>
            <div class="list-item-meta">
              {{ item.case_kind || 'api' }} · {{ item.source }} · {{ item.importance || 'normal' }} · v{{ item.current_version_no || 1 }}
            </div>
            <div v-if="item.health_info?.signals?.length" class="list-item-meta">
              健康度 {{ item.health_info.score }}：{{ item.health_info.signals.join('、') }}
            </div>
          </div>
          <EmptyState
            v-if="!loading && !cases.length"
            :title="hasActiveFilters() ? '当前筛选下暂无 case' : '暂无 case 资产'"
            :description="hasActiveFilters() ? '删除成功或筛选条件过窄会导致列表为空，可清空筛选后查看全部 case。' : '可从需求中心确认 AI 草稿，或在此手动创建 case。'"
          />
        </div>
      </section>

      <aside class="panel-card">
        <div class="panel-card-header">来源追溯 / 版本 / 人工确认</div>
        <div class="panel-card-body">
          <template v-if="selectedCase">
            <div class="chip-row" style="margin-bottom: 12px;">
              <StatusBadge :label="lifecycleLabel" :tone="lifecycleTone" />
              <StatusBadge :label="`当前版本 v${selectedCase.current_version_no || 1}`" tone="neutral" />
            </div>
            <div class="field">
              <label>来源追溯</label>
              <div>接口：{{ selectedCase.api_name || `#${selectedCase.api_id}` }}</div>
              <div>项目 / 模块：{{ selectedCase.project_id || '—' }} / {{ selectedCase.module || '—' }}</div>
              <div>来源文档：{{ selectedCase.source_document?.title || selectedCase.source_document_id || '—' }}</div>
              <div>来源需求点：{{ selectedCase.requirement_item?.title || selectedCase.requirement_item_id || '—' }}</div>
              <div>原文片段：{{ selectedCase.source_excerpt || '—' }}</div>
              <div>来源类型：{{ selectedCase.source }}</div>
            </div>
            <div class="field">
              <label>人工确认记录</label>
              <div>{{ selectedCase.confirmed_by || '—' }} · {{ selectedCase.confirmed_at || '—' }}</div>
              <div v-if="selectedCase.ai_draft">AI 草稿 #{{ selectedCase.ai_draft.id }} · {{ selectedCase.ai_draft.created_by || 'ai' }}</div>
            </div>
            <div class="field">
              <label>结构化步骤</label>
              <ol class="issue-list">
                <li v-for="step in selectedCase.case_steps || []" :key="step.id || step.step_no">
                  {{ step.step_no }}. {{ step.action }}
                </li>
              </ol>
              <div v-if="!(selectedCase.case_steps || []).length" class="list-item-meta">暂无结构化步骤</div>
            </div>
            <div class="field">
              <label>覆盖信息</label>
              <div>类型：{{ selectedCase.category }} · 平台：{{ selectedCase.platform || '—' }}</div>
              <div>版本分组：{{ selectedCase.version_group || '—' }}</div>
              <div>重要性：{{ selectedCase.importance || 'normal' }} · 模块完整交付：{{ selectedCase.module_delivery ? '是' : '否' }}</div>
              <div>待复核：{{ selectedCase.pending_reconfirm ? '是' : '否' }}</div>
            </div>
            <div v-if="selectedCase.lifecycle_status === 'deprecated'" class="field">
              <label>废弃治理</label>
              <div>分类：{{ selectedCase.deprecation_category || '—' }}</div>
              <div>原因：{{ selectedCase.deprecation_reason || '—' }}</div>
              <div>替代 Case：{{ selectedCase.replaced_by_case_id || '—' }}</div>
              <div>变更记录：{{ selectedCase.change_record_id || '—' }}</div>
            </div>
            <div class="field">
              <label>健康度</label>
              <div>{{ selectedCase.health_info?.score ?? 100 }} · {{ selectedCase.health_info?.level || 'good' }}</div>
              <ul v-if="selectedCase.health_info?.signals?.length" class="issue-list">
                <li v-for="signal in selectedCase.health_info.signals" :key="signal">{{ signal }}</li>
              </ul>
            </div>
            <div class="field">
              <label>最近执行摘要</label>
              <div>{{ selectedCase.last_result || '暂无执行记录' }}</div>
            </div>
            <div class="field">
              <label>描述</label>
              <div>{{ selectedCase.description || '—' }}</div>
            </div>
            <div class="field">
              <label>版本历史（{{ versions.length }}）</label>
              <div v-if="versionsLoading" class="list-item-meta">加载中...</div>
              <div v-for="version in versions" :key="version.id" class="version-item">
                <div class="list-item-title">v{{ version.version_no }} · {{ versionDisplayName(version) }}</div>
                <div class="list-item-meta">{{ version.created_at || '—' }} · {{ version.change_reason || '快照' }}</div>
              </div>
              <div v-if="!versionsLoading && !versions.length" class="list-item-meta">暂无历史版本</div>
            </div>
            <div class="toolbar">
              <button type="button" class="btn" @click="openEdit">编辑</button>
              <button type="button" class="btn" @click="submitCopyCase">复制为待确认副本</button>
              <button type="button" class="btn danger" @click="submitDeprecate">废弃 case</button>
            </div>
          </template>
          <template v-else-if="selectedDraft">
            <div class="field">
              <label>用例 ID / 标题</label>
              <div>{{ draftContent.case_no || 'TC-待确认' }} · {{ draftContent.title || selectedDraft.name }}</div>
            </div>
            <div class="field">
              <label>关联需求</label>
              <div>{{ draftContent.requirement_ref || `来源文档 #${selectedDraft.document_id || '—'}` }}</div>
            </div>
            <div class="field">
              <label>前置条件</label>
              <div>{{ draftContent.precondition || '无' }}</div>
            </div>
            <div class="field">
              <label>测试步骤</label>
              <ol class="issue-list">
                <li v-for="(step, index) in draftContent.steps || []" :key="index">{{ step }}</li>
              </ol>
            </div>
            <div class="field">
              <label>预期结果</label>
              <div>{{ draftContent.expected_result || '—' }}</div>
            </div>
            <div class="field">
              <label>重要性 / 类型 / 测试数据</label>
              <div>{{ draftContent.importance || '普通' }} · {{ draftContent.test_type || selectedDraft.case_kind }} · {{ draftContent.test_data || '—' }}</div>
            </div>
            <div class="field">
              <label>来源依据</label>
              <div>{{ draftContent.source_excerpt || selectedDraft.source_excerpt || '—' }}</div>
            </div>
            <div v-if="selectedDraft.reject_reason" class="field">
              <label>高风险拦截原因</label>
              <div>{{ selectedDraft.reject_reason }}</div>
            </div>
            <div class="toolbar">
              <button v-if="selectedDraft.status === 'pending'" type="button" class="btn primary" @click="submitAcceptDraft">接受草稿</button>
              <button type="button" class="btn danger" @click="submitRejectDraft">拒绝</button>
            </div>
          </template>
          <EmptyState v-else title="选择 case 或草稿" description="左侧可查看待确认 AI 草稿，中间为正式 case 列表。" />
        </div>
      </aside>
    </section>

    <div v-if="editorVisible" class="modal-backdrop" @click.self="editorVisible = false">
      <div class="modal">
        <h3>{{ editorMode === 'create' ? '新建 Case' : '编辑 Case' }}</h3>
        <div class="field">
          <label>名称</label>
          <input v-model="editorForm.name" class="input" />
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="editorForm.description" class="textarea" />
        </div>
        <div class="field">
          <label>类型</label>
          <select v-model="editorForm.case_kind" class="select">
            <option value="api">api</option>
            <option value="functional">functional</option>
            <option value="automation">automation</option>
            <option value="mobile">mobile</option>
            <option value="scenario">scenario</option>
          </select>
        </div>
        <div class="field">
          <label>API 归属 ID（手动创建必填，用于绑定项目 / 模块）</label>
          <input v-model="editorForm.api_id" class="input" placeholder="例如：1" />
        </div>
        <div class="field">
          <label>优先级</label>
          <select v-model="editorForm.priority" class="select">
            <option value="P0">P0</option>
            <option value="P1">P1</option>
            <option value="P2">P2</option>
          </select>
        </div>
        <div class="field">
          <label>测试步骤（每行一步，功能/自动化/移动端必填）</label>
          <textarea v-model="editorForm.stepsText" class="textarea" placeholder="1. 打开页面&#10;2. 执行业务操作&#10;3. 校验结果" />
        </div>
        <div class="field">
          <label>预期结果</label>
          <textarea v-model="editorForm.expected_result" class="textarea" placeholder="写明可观察、可判断通过或失败的结果" />
        </div>
        <div class="field">
          <label>接口请求数据 JSON（接口 case 可填）</label>
          <textarea v-model="editorForm.requestDataText" class="textarea" placeholder='{"method":"GET","path":"/users/me"}' />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="editorVisible = false">取消</button>
          <button type="button" class="btn primary" @click="submitEditor">保存</button>
        </div>
      </div>
    </div>

    <div v-if="deprecateVisible" class="modal-backdrop" @click.self="deprecateVisible = false">
      <div class="modal">
        <h3>废弃 Case</h3>
        <div class="field">
          <label>废弃分类</label>
          <select v-model="deprecateForm.category" class="select">
            <option value="FEATURE_REMOVED">功能已移除</option>
            <option value="REDUNDANT">重复 / 冗余</option>
            <option value="FLAKY">不稳定</option>
            <option value="STALE_LOCATOR">元素失效</option>
            <option value="OTHER">其他</option>
          </select>
        </div>
        <div class="field">
          <label>详细原因（不少于 10 字）</label>
          <textarea v-model="deprecateForm.reason" class="textarea" />
        </div>
        <div class="field">
          <label>替代 Case ID（冗余废弃必填）</label>
          <input v-model="deprecateForm.replaced_by_case_id" class="input" placeholder="例如：123" />
        </div>
        <div class="field">
          <label>变更记录 ID（功能移除 / 元素失效必填）</label>
          <input v-model="deprecateForm.change_record_id" class="input" placeholder="例如：456" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="deprecateVisible = false">取消</button>
          <button type="button" class="btn danger" @click="submitDeprecateForm">确认废弃</button>
        </div>
      </div>
    </div>

    <div v-if="rejectVisible" class="modal-backdrop" @click.self="rejectVisible = false">
      <div class="modal">
        <h3>拒绝 AI 草稿</h3>
        <div class="field">
          <label>拒绝分类</label>
          <select v-model="rejectForm.category" class="select">
            <option value="LOGIC_ERROR">逻辑错误</option>
            <option value="MISSING_ASSERTION">缺少断言</option>
            <option value="OUT_OF_SCOPE">超出需求范围</option>
            <option value="DUPLICATE">重复</option>
            <option value="HALLUCINATION">AI 幻觉</option>
            <option value="FORMAT_ERROR">格式错误</option>
            <option value="OTHER">其他</option>
          </select>
        </div>
        <div class="field">
          <label>详细原因（不少于 10 字，将进入负样本库）</label>
          <textarea v-model="rejectForm.reason" class="textarea" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="rejectVisible = false">取消</button>
          <button type="button" class="btn danger" @click="submitRejectDraftForm">确认拒绝</button>
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
  acceptCaseDraft,
  copyCase,
  createCase,
  deprecateCase,
  fetchCaseDetail,
  fetchCaseDrafts,
  fetchCases,
  fetchCaseVersions,
  rejectCaseDraft,
  updateCase,
} from '../api.js'

const loading = ref(false)
const versionsLoading = ref(false)
const cases = ref([])
const drafts = ref([])
const versions = ref([])
const total = ref(0)
const selectedId = ref(null)
const selectedDraftId = ref(null)
const selectedDraft = ref(null)
const selectedCase = ref(null)
const message = ref('')
const messageTone = ref('info')
const editorVisible = ref(false)
const deprecateVisible = ref(false)
const rejectVisible = ref(false)
const editorMode = ref('create')
const filters = reactive({
  keyword: '',
  case_kind: '',
  source: '',
  lifecycle_status: 'active',
  importance: '',
  module_delivery: false,
})
const editorForm = reactive({
  api_id: '',
  name: '',
  description: '',
  case_kind: 'functional',
  priority: 'P1',
  stepsText: '',
  expected_result: '',
  requestDataText: '',
})
const deprecateForm = reactive({
  category: 'OTHER',
  reason: '',
  replaced_by_case_id: '',
  change_record_id: '',
})
const rejectForm = reactive({
  category: 'OTHER',
  reason: '',
})

const lifecycleLabel = computed(() => {
  const status = selectedCase.value?.lifecycle_status || 'active'
  return status === 'deprecated' ? '已废弃' : '活跃资产'
})
const lifecycleTone = computed(() => (selectedCase.value?.lifecycle_status === 'deprecated' ? 'danger' : 'success'))
const draftContent = computed(() => selectedDraft.value?.structured_content || {})

function showMessage(text, tone = 'info') {
  message.value = text
  messageTone.value = tone
}

function hasActiveFilters() {
  return Boolean(filters.keyword || filters.case_kind || filters.source || filters.lifecycle_status !== 'active' || filters.importance || filters.module_delivery)
}

function versionDisplayName(version) {
  return version?.snapshot?.name || version?.name || '未命名'
}

function normalizeCaseListResponse(response) {
  if (!response) return { items: [], total: 0 }
  if (Array.isArray(response)) {
    return { items: response, total: response.length }
  }
  const items = Array.isArray(response.items) ? response.items : []
  const total = typeof response.total === 'number' ? response.total : items.length
  return { items, total }
}

async function loadDrafts() {
  try {
    const [pendingResponse, blockedResponse] = await Promise.all([
      fetchCaseDrafts(new URLSearchParams({ status: 'pending' })),
      fetchCaseDrafts(new URLSearchParams({ status: 'check_failed' })),
    ])
    drafts.value = [...(pendingResponse.items || []), ...(blockedResponse.items || [])]
    if (selectedDraftId.value && !drafts.value.some((item) => item.id === selectedDraftId.value)) {
      selectedDraftId.value = null
      selectedDraft.value = null
    }
  } catch {
    drafts.value = []
  }
}

async function loadCases() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.keyword) params.set('keyword', filters.keyword)
    if (filters.case_kind) params.set('case_kind', filters.case_kind)
    if (filters.source) params.set('source', filters.source)
    if (filters.lifecycle_status) params.set('lifecycle_status', filters.lifecycle_status)
    if (filters.lifecycle_status !== 'active') params.set('include_deprecated', 'true')
    if (filters.importance) params.set('importance', filters.importance)
    if (filters.module_delivery) params.set('module_delivery', '1')
    const response = normalizeCaseListResponse(await fetchCases(params))
    cases.value = response.items
    total.value = response.total
    if (selectedId.value && !cases.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = null
      selectedCase.value = null
      versions.value = []
    }
    if (!selectedId.value && cases.value[0]) {
      await selectCase(cases.value[0].id)
    }
  } catch (error) {
    showMessage(`加载 Case 列表失败：${error.message}`, 'danger')
  } finally {
    loading.value = false
  }
}

async function loadVersions(caseId) {
  versionsLoading.value = true
  try {
    const response = await fetchCaseVersions(caseId)
    versions.value = response.items || []
  } catch {
    versions.value = []
  } finally {
    versionsLoading.value = false
  }
}

function selectDraft(draftId) {
  selectedDraftId.value = draftId
  selectedId.value = null
  selectedCase.value = null
  selectedDraft.value = drafts.value.find((item) => item.id === draftId) || null
}

async function selectCase(caseId) {
  selectedId.value = caseId
  selectedDraftId.value = null
  selectedDraft.value = null
  try {
    selectedCase.value = await fetchCaseDetail(caseId)
    await loadVersions(caseId)
  } catch (error) {
    showMessage(`加载 Case 详情失败：${error.message}`, 'danger')
  }
}

function openCreate() {
  editorMode.value = 'create'
  editorForm.api_id = ''
  editorForm.name = ''
  editorForm.description = ''
  editorForm.case_kind = 'functional'
  editorForm.priority = 'P1'
  editorForm.stepsText = ''
  editorForm.expected_result = ''
  editorForm.requestDataText = ''
  editorVisible.value = true
}

function openEdit() {
  if (!selectedCase.value) return
  editorMode.value = 'edit'
  editorForm.api_id = selectedCase.value.api_id ? String(selectedCase.value.api_id) : ''
  editorForm.name = selectedCase.value.name
  editorForm.description = selectedCase.value.description || ''
  editorForm.case_kind = selectedCase.value.case_kind || 'functional'
  editorForm.priority = selectedCase.value.priority || 'P1'
  editorForm.stepsText = (selectedCase.value.steps || []).join('\n')
  editorForm.expected_result = selectedCase.value.expected_result || ''
  editorForm.requestDataText = selectedCase.value.request_data && Object.keys(selectedCase.value.request_data).length
    ? JSON.stringify(selectedCase.value.request_data, null, 2)
    : ''
  editorVisible.value = true
}

async function submitEditor() {
  if (!editorForm.name.trim()) {
    showMessage('Case 名称不能为空', 'danger')
    return
  }
  let requestData = {}
  if (editorForm.requestDataText.trim()) {
    try {
      requestData = JSON.parse(editorForm.requestDataText)
    } catch {
      showMessage('接口请求数据必须是合法 JSON', 'danger')
      return
    }
  }
  const payload = {
    api_id: editorForm.api_id ? Number(editorForm.api_id) : null,
    name: editorForm.name,
    description: editorForm.description,
    case_kind: editorForm.case_kind,
    priority: editorForm.priority,
    steps: editorForm.stepsText.split('\n').map((item) => item.trim()).filter(Boolean),
    expected_result: editorForm.expected_result,
    request_data: requestData,
  }
  try {
    if (editorMode.value === 'create') {
      await createCase(payload)
      showMessage('Case 创建成功', 'success')
    } else {
      await updateCase(selectedId.value, payload)
      showMessage('Case 更新成功，已生成新版本快照', 'success')
    }
    editorVisible.value = false
    await loadCases()
    if (selectedId.value) await selectCase(selectedId.value)
  } catch (error) {
    showMessage(`保存失败：${error.message}`, 'danger')
  }
}

async function submitDeprecate() {
  if (!selectedId.value) return
  deprecateForm.category = 'OTHER'
  deprecateForm.reason = ''
  deprecateForm.replaced_by_case_id = ''
  deprecateForm.change_record_id = ''
  deprecateVisible.value = true
}

async function submitDeprecateForm() {
  if (!selectedId.value) return
  if (deprecateForm.reason.trim().length < 10) {
    showMessage('废弃原因不能少于 10 字', 'danger')
    return
  }
  try {
    await deprecateCase(selectedId.value, {
      category: deprecateForm.category,
      reason: deprecateForm.reason,
      replaced_by_case_id: deprecateForm.replaced_by_case_id ? Number(deprecateForm.replaced_by_case_id) : null,
      change_record_id: deprecateForm.change_record_id ? Number(deprecateForm.change_record_id) : null,
    })
    deprecateVisible.value = false
    selectedId.value = null
    selectedCase.value = null
    versions.value = []
    showMessage('Case 已废弃，不再出现在正式资产列表', 'success')
    await loadCases()
  } catch (error) {
    showMessage(`废弃失败：${error.message}`, 'danger')
  }
}

async function submitCopyCase() {
  if (!selectedId.value) return
  try {
    const copied = await copyCase(selectedId.value, { copied_by: 'frontend' })
    showMessage('已复制为待确认副本', 'success')
    await loadCases()
    await selectCase(copied.id)
  } catch (error) {
    showMessage(`复制失败：${error.message}`, 'danger')
  }
}

async function submitAcceptDraft() {
  if (!selectedDraftId.value) return
  try {
    await acceptCaseDraft(selectedDraftId.value)
    showMessage('草稿已接受并写入正式 case 库', 'success')
    selectedDraftId.value = null
    selectedDraft.value = null
    await Promise.all([loadDrafts(), loadCases()])
  } catch (error) {
    showMessage(`接受失败：${error.message}`, 'danger')
  }
}

async function submitRejectDraft() {
  if (!selectedDraftId.value) return
  rejectForm.category = 'OTHER'
  rejectForm.reason = ''
  rejectVisible.value = true
}

async function submitRejectDraftForm() {
  if (!selectedDraftId.value) return
  if (rejectForm.reason.trim().length < 10) {
    showMessage('拒绝原因不能少于 10 字', 'danger')
    return
  }
  try {
    await rejectCaseDraft(selectedDraftId.value, { ...rejectForm })
    rejectVisible.value = false
    showMessage('草稿已拒绝并进入负样本记录', 'success')
    selectedDraftId.value = null
    selectedDraft.value = null
    await loadDrafts()
  } catch (error) {
    showMessage(`拒绝失败：${error.message}`, 'danger')
  }
}

onMounted(async () => {
  await loadDrafts()
  await loadCases()
})
</script>
