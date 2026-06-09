<template>
  <div>
    <PageHeader
      title="需求资产工作台"
      subtitle="需求中心是测试资产链路的事实源。只有检查通过并入库的文档，才能作为 case 生成依据。"
    >
      <template #actions>
        <button type="button" class="btn" @click="toggleTrashView">
          {{ showTrash ? '返回活跃文档' : '回收站 / 归档' }}
        </button>
        <button type="button" class="btn primary" @click="openUploadModal">上传需求文档</button>
      </template>
    </PageHeader>

    <div v-if="message" class="message" :class="messageTone">{{ message }}</div>

    <section class="workspace-layout requirement-workspace-layout">
      <aside class="panel-card">
        <div class="panel-card-header">
          <span>需求关系树</span>
          <button type="button" class="btn btn-sm" @click="openTreeEditor('create-root')">新增域</button>
        </div>
        <div class="panel-card-body">
          <div
            class="tree-node"
            :class="{ selected: selectedTreeNodeId === null && !showTrash }"
            @click="selectTreeNode(null)"
          >
            全部需求文档
          </div>
          <div
            v-for="node in flatTreeNodes"
            :key="node.id"
            class="tree-node"
            :class="{ child: node.level > 0, selected: selectedTreeNodeId === node.id }"
            :style="{ paddingLeft: `${8 + node.level * 14}px` }"
            @click="selectTreeNode(node.id)"
          >
            <span class="tree-node-type">{{ nodeTypeLabel(node.node_type) }}</span>
            {{ node.name }}
          </div>
          <EmptyState v-if="!flatTreeNodes.length" title="暂无关系树节点" description="点击「新增域」创建业务域，再逐级添加模块与功能。" />
          <div v-if="selectedTreeNodeId && !showTrash" class="toolbar tree-toolbar">
            <button type="button" class="btn btn-sm" @click="openTreeEditor('create-child')">子节点</button>
            <button type="button" class="btn btn-sm" @click="openTreeEditor('edit')">编辑</button>
            <button type="button" class="btn btn-sm danger" @click="removeTreeNode">删除</button>
          </div>
        </div>
      </aside>

      <section class="panel-card">
        <div class="panel-card-header">{{ showTrash ? '回收站 / 归档' : '需求文档列表' }}</div>
        <div class="panel-card-body">
          <div v-if="!showTrash" class="toolbar">
            <input v-model="keyword" class="input" placeholder="搜索标题或模块" @keyup.enter="loadDocuments" />
            <select v-model="categoryFilter" class="select">
              <option value="">全部分类</option>
              <option v-for="item in categoryOptions" :key="item" :value="item">{{ item }}</option>
            </select>
            <button type="button" class="btn" @click="loadDocuments">查询</button>
          </div>
          <div v-if="loading" class="empty-state">加载中...</div>
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="list-item"
            :class="{ selected: selectedId === doc.id }"
            @click="selectDocument(doc.id)"
          >
            <div class="list-item-title">{{ doc.title }}</div>
            <div class="list-item-meta">
              {{ doc.category || '未分类' }} · {{ doc.module || '未挂载模块' }}
              <StatusBadge v-if="!showTrash" :label="parseStatusLabel(doc.parse_status)" :tone="parseStatusTone(doc.parse_status)" />
            </div>
          </div>
          <EmptyState
            v-if="!loading && !documents.length"
            :title="showTrash ? '回收站为空' : '暂无需求文档'"
            :description="showTrash ? '已删除或归档的文档会出现在这里。' : '上传 PDF / Word / Markdown 文档开始建立需求资产库。'"
          />
        </div>
      </section>

      <aside class="panel-card requirement-detail-panel">
        <div class="panel-card-header">解析工作区 / 入库门禁</div>
        <div class="panel-card-body">
          <template v-if="selectedDocument">
            <div class="detail-hero">
              <div>
                <div class="chip-row">
                  <StatusBadge label="解析与入库门禁" :tone="gateTone" />
                  <StatusBadge v-if="!showTrash" :label="parseStatusLabel(selectedDocument.parse_status)" :tone="parseStatusTone(selectedDocument.parse_status)" />
                </div>
                <h3>{{ selectedDocument.title }}</h3>
                <p>检查未通过不得生成 case；AI 草稿需人工确认。</p>
              </div>
              <div class="detail-metrics">
                <div>
                  <strong>{{ requirementItems.length }}</strong>
                  <span>需求点</span>
                </div>
                <div>
                  <strong>{{ parseIssues.length }}</strong>
                  <span>待优化</span>
                </div>
                <div>
                  <strong>{{ reviewRequirementItems.length }}</strong>
                  <span>需复核</span>
                </div>
              </div>
            </div>
            <div v-if="parsePayload?.document_type" class="parse-route-card">
              <strong>当前解析绑定：{{ documentTypeLabel(parsePayload.document_type) }}</strong>
              <span>使用 {{ parsePayload.parser_skill || '默认解析 Skill' }}</span>
            </div>

            <div class="detail-grid">
              <div v-if="!showTrash && treePathLabel" class="field col-span-2">
                <label>需求树路径</label>
                <div class="tree-path-text">{{ treePathLabel }}</div>
              </div>
              <div v-if="!showTrash" class="field">
                <label>挂载节点</label>
                <select v-model="mountNodeId" class="select" :disabled="actionLoading" @change="submitMountFromDetail">
                  <option :value="null">未挂载</option>
                  <option v-for="node in flatTreeNodes" :key="node.id" :value="node.id">
                    {{ treeNodeOptionLabel(node) }}
                  </option>
                </select>
              </div>
              <div v-if="!showTrash" class="field">
                <label>业务文档分类</label>
                <select v-model="selectedCategory" class="select" :disabled="actionLoading" @change="submitCategoryChangeFromDetail">
                  <option v-for="item in categoryOptions" :key="item" :value="item">
                    {{ item }}
                  </option>
                </select>
              </div>
            </div>

            <div v-if="documentRelations" class="field summary-card">
              <label>关系视图</label>
              <div>
                关联 Case：{{ documentRelations.cases?.length || 0 }} ·
                API：{{ documentRelations.apis?.length || 0 }} ·
                模块：{{ (documentRelations.modules || []).join('、') || '—' }} ·
                变更记录：{{ documentRelations.changes?.length || 0 }}
              </div>
            </div>

            <div class="field summary-card" :class="{ warning: aiSummaryUnavailable }">
              <label>AI 摘要</label>
              <div>{{ aiSummaryText }}</div>
              <p v-if="aiSummaryUnavailable">摘要生成超时或调用失败，不影响文档解析与入库门禁；解析完成后会使用规则摘要补位。</p>
            </div>

            <div v-if="parseIssues.length" class="field issue-workbench">
              <div class="issue-alert">
                <div>
                  <strong>待优化 / 需人工关注（{{ parseIssues.length }}）</strong>
                  <p>每条问题单独处理；确认入库前必须处理阻断项。</p>
                </div>
                <div class="issue-card-list">
                  <article
                    v-for="(issue, index) in parseIssues"
                    :key="index"
                    class="issue-card"
                    :class="[issueClass(issue), { selected: selectedIssueIndex === index }]"
                    @click="selectIssue(index)"
                  >
                    <div class="issue-card-header">
                      <div class="chip-row">
                        <span class="issue-tag">{{ issueTypeLabel(issue) }}</span>
                        <span class="issue-tag">{{ issueSeverityLabel(issue) }}</span>
                        <span v-if="issue?.blocking" class="issue-tag danger">阻断</span>
                      </div>
                      <strong>{{ formatIssue(issue) }}</strong>
                    </div>
                    <div v-if="issueDetailText(issue)" class="list-item-meta">{{ issueDetailText(issue) }}</div>
                    <div class="issue-card-body">
                      <div v-if="issue?.source_excerpt" class="source-excerpt">原文：{{ issue.source_excerpt }}</div>
                      <div v-if="issue?.ai_reason" class="source-excerpt">AI 判断：{{ issue.ai_reason }}</div>
                      <div v-if="issue?.suggestion" class="source-excerpt">建议：{{ issue.suggestion }}</div>
                      <div v-if="!(issue?.source_excerpt || issue?.suggestion || issue?.ai_reason)" class="list-item-meta">暂无更多依据或建议</div>
                    </div>
                    <div class="issue-card-actions">
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="openIssueEditor('modify', index)">修改原文片段</button>
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="submitAcceptSuggestion(index)">采纳 AI 建议</button>
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="openIssueEditor('ignore', index)">忽略并留痕</button>
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="submitManualReview(index)">转人工确认</button>
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="submitResolveIssue(index)">标记已解决</button>
                      <button type="button" class="btn btn-sm" :disabled="actionLoading || !issue?.id" @click.stop="submitIssueRecheck(index)">重新检查</button>
                    </div>
                  </article>
                </div>
              </div>
              <div v-if="reviewRequirementItems.length" class="linked-review-card">
                <strong>关联需复核需求点（{{ reviewRequirementItems.length }}）</strong>
                <span>{{ selectedIssue ? `当前问题：${formatIssue(selectedIssue)}` : '优先处理标记为需复核的需求点。' }}</span>
              </div>
            </div>

            <div v-if="requirementRevisions.length" class="field">
              <label>文档修订版（{{ requirementRevisions.length }}）</label>
              <div v-for="revision in requirementRevisions" :key="revision.id" class="version-item">
                <div class="list-item-title">v{{ revision.revision_no }} · 问题项 #{{ revision.issue_id || '—' }}</div>
                <div class="list-item-meta">{{ revision.created_by || 'system' }} · {{ revision.created_at || '—' }}</div>
                <details>
                  <summary>查看修订片段</summary>
                  <div class="source-excerpt">{{ revision.revised_excerpt }}</div>
                </details>
              </div>
            </div>

            <div v-if="historyDiffItems.length" class="field">
              <label>历史需求对比（{{ historyDiffItems.length }}）</label>
              <div v-for="(item, index) in historyDiffItems" :key="index" class="version-item">
                <div class="list-item-title">{{ historyDiffLabel(item.change_type) }}</div>
                <div class="list-item-meta">{{ historyDiffSummary(item) }}</div>
              </div>
            </div>

            <div v-if="couplingItems.length" class="field">
              <label>业务耦合检查（{{ couplingItems.length }}）</label>
              <div v-for="(item, index) in couplingItems" :key="index" class="version-item">
                <div class="list-item-title">{{ item.requirement_no || 'DOCUMENT' }} · {{ item.title }}</div>
                <div class="list-item-meta">
                  依赖范围：{{ (item.dependency_scope || []).join('、') || '未指定' }}
                </div>
                <div v-if="item.dependency_notes" class="source-excerpt">{{ item.dependency_notes }}</div>
              </div>
            </div>

            <div v-if="requirementItems.length" class="field">
              <label>结构化需求点（{{ requirementItems.length }}）</label>
              <div class="requirement-tab-list">
                <details class="requirement-tab-panel success" open>
                  <summary>
                    <span>检查通过</span>
                    <strong>{{ approvedRequirementItems.length }}</strong>
                  </summary>
                  <div v-if="approvedRequirementItems.length" class="requirement-card-list">
                    <article
                      v-for="item in approvedRequirementItems"
                      :key="item.id || item.requirement_no || item.title"
                      :id="'req-card-' + item.requirement_no"
                      class="requirement-card"
                      :class="{ highlighted: item.requirement_no === selectedIssueRequirementNo }"
                    >
                      <div class="requirement-card-header">
                        <strong>{{ requirementItemTitle(item) }}</strong>
                        <div class="chip-row">
                          <span class="mini-chip">{{ item.priority || 'P1' }}</span>
                          <span class="mini-chip">{{ requirementTypeLabel(item.item_type) }}</span>
                          <span class="mini-chip success">可确认</span>
                        </div>
                      </div>
                      <p>{{ item.content || '暂无需求内容' }}</p>
                      <details v-if="item.source_text">
                        <summary>查看原文依据</summary>
                        <div class="source-excerpt">{{ item.source_text }}</div>
                      </details>
                    </article>
                  </div>
                  <EmptyState v-else title="暂无检查通过需求点" description="当前解析结果中的需求点都需要人工确认。" />
                </details>

                <details class="requirement-tab-panel warning" :open="reviewRequirementItems.length > 0">
                  <summary>
                    <span>待确认（需复核项已同步到上方问题项卡片）</span>
                    <strong>{{ reviewRequirementItems.length }}</strong>
                  </summary>
                  <div v-if="reviewRequirementItems.length" class="list-item-meta review-routing-hint">
                    这些需复核项已同步到上方“待优化 / 需人工关注”卡片，请在那里完成修改、忽略、转人工或重新检查。
                  </div>
                  <div v-if="reviewRequirementItems.length" class="requirement-card-list">
                    <article
                      v-for="item in reviewRequirementItems"
                      :key="item.id || item.requirement_no || item.title"
                      :id="'req-card-' + item.requirement_no"
                      class="requirement-card need-review"
                      :class="{ highlighted: item.requirement_no === selectedIssueRequirementNo }"
                    >
                      <div class="requirement-card-header">
                        <strong>{{ requirementItemTitle(item) }}</strong>
                        <div class="chip-row">
                          <span class="mini-chip">{{ item.priority || 'P1' }}</span>
                          <span class="mini-chip">{{ requirementTypeLabel(item.item_type) }}</span>
                          <span class="mini-chip danger">需复核</span>
                        </div>
                      </div>
                      <p>{{ item.content || '暂无需求内容' }}</p>
                      <details v-if="item.source_text">
                        <summary>查看原文依据</summary>
                        <div class="source-excerpt">{{ item.source_text }}</div>
                      </details>
                    </article>
                  </div>
                  <EmptyState v-else title="暂无待确认需求点" description="当前结构化需求点均已通过规则检查。" />
                </details>
              </div>
            </div>
            <div v-else-if="analysis" class="field">
              <label>结构化解析结果</label>
              <div class="preview-box">{{ JSON.stringify(analysis, null, 2) }}</div>
            </div>
            <details class="field raw-preview">
              <summary>展开原文预览</summary>
              <div class="preview-box">{{ selectedDocument.extracted_content || '暂无原文内容' }}</div>
            </details>
            <div v-if="!showTrash" class="toolbar">
              <button type="button" class="btn" :disabled="actionLoading" @click="downloadSelectedDocument">
                下载原文
              </button>
              <button
                v-if="canParse"
                type="button"
                class="btn primary"
                :disabled="actionLoading"
                @click="submitParse"
              >
                触发解析
              </button>
              <button
                v-if="canConfirm"
                type="button"
                class="btn primary"
                :disabled="actionLoading"
                @click="submitConfirm"
              >
                确认入库
              </button>
              <button
                type="button"
                class="btn"
                :disabled="actionLoading"
                @click="submitRecheck"
              >
                重新检查
              </button>
              <button
                v-if="canGenerateCases"
                type="button"
                class="btn primary"
                :disabled="actionLoading"
                @click="submitGenerateCases"
              >
                生成 case 草稿
              </button>
              <button type="button" class="btn" :disabled="actionLoading" @click="openMoveDialog">
                移动节点
              </button>
              <button type="button" class="btn" :disabled="actionLoading" @click="submitArchive">归档</button>
              <button type="button" class="btn danger" :disabled="actionLoading" @click="submitSoftDelete">移入回收站</button>
            </div>
            <div v-else class="toolbar">
              <button type="button" class="btn primary" :disabled="actionLoading" @click="submitRestore">恢复文档</button>
            </div>
          </template>
          <EmptyState v-else title="选择文档查看详情" description="右侧将展示原文预览、解析摘要与入库门禁说明。" />
        </div>
      </aside>
    </section>

    <div v-if="uploadVisible" class="modal-backdrop" @click.self="uploadVisible = false">
      <div class="modal">
        <h3>上传需求文档</h3>
        <div class="field">
          <label>标题</label>
          <input v-model="uploadForm.title" class="input" placeholder="可选，默认使用文件名" />
        </div>
        <div class="field">
          <label>分类</label>
          <select v-model="uploadForm.category" class="select">
            <option v-for="item in categoryOptions" :key="item" :value="item">
              {{ item }}
            </option>
          </select>
          <p class="form-help">{{ categoryDescription(uploadForm.category) }}</p>
          <div class="category-guide">
            <div v-for="item in defaultCategoryGuides" :key="item.name">
              <strong>{{ item.name }}</strong>
              <span>{{ item.description }}</span>
            </div>
          </div>
        </div>
        <div class="field">
          <label>模块</label>
          <input v-model="uploadForm.module" class="input" placeholder="例如：登录模块" />
        </div>
        <div class="field">
          <label>挂载到关系树节点</label>
          <select v-model="uploadForm.tree_node_id" class="select">
            <option :value="null">不挂载（稍后可在详情中设置）</option>
            <option v-for="node in flatTreeNodes" :key="node.id" :value="node.id">
              {{ treeNodeOptionLabel(node) }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>文件</label>
          <input type="file" class="input" @change="onFileChange" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="uploadVisible = false">取消</button>
          <button type="button" class="btn primary" :disabled="uploading" @click="submitUpload">上传</button>
        </div>
      </div>
    </div>

    <div v-if="treeEditorVisible" class="modal-backdrop" @click.self="treeEditorVisible = false">
      <div class="modal">
        <h3>{{ treeEditorTitle }}</h3>
        <div class="field">
          <label>节点名称</label>
          <input v-model="treeForm.name" class="input" placeholder="例如：认证中心" />
        </div>
        <div class="field">
          <label>节点类型</label>
          <select v-model="treeForm.node_type" class="select" :disabled="treeEditorMode === 'edit'">
            <option value="domain">业务域</option>
            <option value="module">模块</option>
            <option value="feature">功能</option>
            <option value="version">版本</option>
            <option value="acceptance_point">验收点</option>
          </select>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="treeEditorVisible = false">取消</button>
          <button type="button" class="btn primary" @click="submitTreeEditor">保存</button>
        </div>
      </div>
    </div>

    <div v-if="moveDialogVisible" class="modal-backdrop" @click.self="moveDialogVisible = false">
      <div class="modal">
        <h3>移动文档节点</h3>
        <div class="field">
          <label>当前节点</label>
          <div>{{ treePathLabel || '未挂载' }}</div>
        </div>
        <div class="field">
          <label>目标节点</label>
          <select v-model="moveForm.target_tree_node_id" class="select">
            <option :value="null">未挂载</option>
            <option v-for="node in flatTreeNodes" :key="node.id" :value="node.id">
              {{ treeNodeOptionLabel(node) }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="moveDialogVisible = false">取消</button>
          <button type="button" class="btn primary" :disabled="actionLoading" @click="submitMoveDocument">确认移动</button>
        </div>
      </div>
    </div>

    <div v-if="issueEditorVisible" class="modal-backdrop" @click.self="issueEditorVisible = false">
      <div class="modal">
        <h3>{{ issueEditorMode === 'modify' ? '修改文档问题项' : '忽略文档问题项' }}</h3>
        <div v-if="selectedIssue" class="field">
          <label>问题说明</label>
          <div>{{ formatIssue(selectedIssue) }}</div>
        </div>
        <div v-if="issueEditorMode === 'modify'" class="field">
          <label>修订后的原文片段</label>
          <textarea v-model="issueForm.revised_excerpt" class="textarea" />
        </div>
        <div class="field">
          <label>{{ issueEditorMode === 'modify' ? '修改原因' : '忽略原因（不少于 10 字）' }}</label>
          <textarea v-model="issueForm.reason" class="textarea" />
        </div>
        <label v-if="issueEditorMode === 'ignore'" class="list-item-meta">
          <input v-model="issueForm.risk_accepted" type="checkbox" />
          已确认风险并留痕，允许忽略该问题
        </label>
        <div class="modal-actions">
          <button type="button" class="btn" @click="issueEditorVisible = false">取消</button>
          <button type="button" class="btn primary" :disabled="actionLoading" @click="submitIssueEditor">提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, nextTick } from 'vue'
import PageHeader from '../../../shared/components/PageHeader.vue'
import StatusBadge from '../../../shared/components/StatusBadge.vue'
import EmptyState from '../../../shared/components/EmptyState.vue'
import { API_BASE } from '../../../shared/api/http.js'
import {
  acceptRequirementIssueSuggestion,
  archiveDocument,
  confirmDocument,
  createTreeNode,
  deleteTreeNode,
  fetchRequirementCategories,
  fetchRequirementDocumentAnalysis,
  fetchRequirementDocumentDetail,
  fetchRequirementDocuments,
  fetchRequirementIssues,
  fetchRequirementItems,
  fetchRequirementRevisions,
  fetchRequirementTree,
  fetchDocumentImpact,
  fetchDocumentRelations,
  fetchDocumentTreePath,
  fetchTrashDocuments,
  generateCasesFromDocument,
  manualReviewRequirementIssue,
  mountDocument,
  moveDocument,
  modifyRequirementIssue,
  ignoreRequirementIssue,
  parseDocument,
  recheckRequirementIssue,
  recheckRequirementDocument,
  resolveRequirementIssue,
  restoreDocument,
  softDeleteDocument,
  updateTreeNode,
  uploadRequirementDocument,
  updateDocumentMeta,
} from '../api.js'

const loading = ref(false)
const actionLoading = ref(false)
const uploading = ref(false)
const uploadVisible = ref(false)
const treeEditorVisible = ref(false)
const moveDialogVisible = ref(false)
const issueEditorVisible = ref(false)
const issueEditorMode = ref('modify')
const treeEditorMode = ref('create-root')
const showTrash = ref(false)
const keyword = ref('')
const categoryFilter = ref('')
const treePathLabel = ref('')
const documents = ref([])
const treeItems = ref([])
const categories = ref([])
const selectedTreeNodeId = ref(null)
const selectedId = ref(null)
const selectedDocument = ref(null)
const analysis = ref(null)
const parsePayload = ref(null)
const requirementItems = ref([])
const parseIssues = ref([])
const requirementRevisions = ref([])
const documentRelations = ref(null)
const selectedIssueIndex = ref(null)
const message = ref('')
const messageTone = ref('info')
const mountNodeId = ref(null)
const selectedCategory = ref('未分类')
const uploadForm = reactive({
  title: '',
  category: '未分类',
  module: '',
  tree_node_id: null,
  file: null,
})
const treeForm = reactive({
  name: '',
  node_type: 'domain',
})
const moveForm = reactive({
  from_tree_node_id: null,
  target_tree_node_id: null,
})
const issueForm = reactive({
  revised_excerpt: '',
  reason: '',
  risk_accepted: false,
})

const NODE_TYPE_LABELS = {
  domain: '域',
  module: '模块',
  feature: '功能',
  version: '版本',
  acceptance_point: '验收点',
}

const DEFAULT_CATEGORIES = ['未分类', '需求文档', '测试需求说明', '接口文档', '线上接口 Log', '变更说明', '验收标准']
const CATEGORY_DESCRIPTIONS = {
  未分类: '临时导入或暂不确定类型的资料；建议解析前补充为明确分类。',
  需求文档: '业务规则、用户故事、功能说明，默认绑定 RequirementParseSkill。',
  测试需求说明: '测试范围、测试目标、验收重点和测试约束说明，可作为 case 生成输入。',
  接口文档: 'OpenAPI、Swagger、接口总览表或 Method/Path 文档，默认绑定 ApiDocumentParseSkill。',
  '线上接口 Log': '生产或测试环境接口访问日志、异常日志，默认绑定 ApiLogParseSkill。',
  变更说明: '版本差异、需求变更、发布说明，用于历史对比和影响分析。',
  验收标准: '验收口径、通过条件、Definition of Done，用于补齐 case 预期结果。',
}

const PARSE_STATUS = {
  unparsed: { label: '未解析', tone: 'neutral' },
  parsing: { label: '解析中', tone: 'warning' },
  pending_review: { label: '待确认', tone: 'warning' },
  check_failed: { label: '检查失败', tone: 'danger' },
  stored: { label: '已入库', tone: 'success' },
}

function flattenTree(items, level = 0) {
  const result = []
  for (const node of items || []) {
    result.push({ ...node, level })
    result.push(...flattenTree(node.children, level + 1))
  }
  return result
}

const flatTreeNodes = computed(() => flattenTree(treeItems.value))
const categoryOptions = computed(() => {
  const merged = new Set([...DEFAULT_CATEGORIES, ...categories.value])
  return [...merged]
})
const defaultCategoryGuides = computed(() => DEFAULT_CATEGORIES.filter((item) => item !== '未分类').map((name) => ({
  name,
  description: CATEGORY_DESCRIPTIONS[name],
})))
const treeNodeMap = computed(() => Object.fromEntries(flatTreeNodes.value.map((node) => [node.id, node])))
const treeEditorTitle = computed(() => {
  if (treeEditorMode.value === 'edit') return '编辑树节点'
  if (treeEditorMode.value === 'create-child') return '新增子节点'
  return '新增业务域'
})
const gateTone = computed(() => (selectedDocument.value?.parse_status === 'stored' ? 'success' : 'warning'))
const canParse = computed(() => {
  const status = selectedDocument.value?.parse_status
  return status === 'unparsed' || status === 'check_failed' || status === 'stored'
})
const canConfirm = computed(() => selectedDocument.value?.parse_status === 'pending_review')
const canGenerateCases = computed(() => selectedDocument.value?.parse_status === 'stored')
const aiSummaryUnavailable = computed(() => isAiSummaryFailure(selectedDocument.value?.ai_summary))
const aiSummaryText = computed(() => {
  if (aiSummaryUnavailable.value) return 'AI 摘要暂不可用'
  return selectedDocument.value?.ai_summary || '暂无摘要，上传后会在后台生成；也可先触发结构化解析。'
})
const approvedRequirementItems = computed(() => requirementItems.value.filter((item) => !item.need_review))
const reviewRequirementItems = computed(() => requirementItems.value.filter((item) => item.need_review))
const selectedIssue = computed(() => (
  selectedIssueIndex.value === null ? null : parseIssues.value[selectedIssueIndex.value]
))
const selectedIssueId = computed(() => selectedIssue.value?.id || null)
const selectedIssueRequirementNo = computed(() => {
  if (!selectedIssue.value) return null
  const issue = selectedIssue.value
  if (issue.requirement_no) return issue.requirement_no
  if (issue.source_location) return issue.source_location
  
  const msg = typeof issue === 'string' ? issue : (issue.message || '')
  const reqNoMatch = msg.match(/(REQ-\d+|API-\d+)/)
  return reqNoMatch ? reqNoMatch[0] : null
})
const historyDiffItems = computed(() => parsePayload.value?.history_diff?.diff_items || [])
const couplingItems = computed(() => parsePayload.value?.coupling_results?.items || [])

function treeNodeOptionLabel(node) {
  const indent = node.level > 0 ? `${'　'.repeat(node.level)}` : ''
  const count = Number.isFinite(node.document_count) ? `（${node.document_count} 文档）` : ''
  return `${indent}${nodeTypeLabel(node.node_type)} · ${node.name}${count}`
}

function nodeTypeLabel(type) {
  return NODE_TYPE_LABELS[type] || type
}

function parseStatusLabel(status) {
  return PARSE_STATUS[status]?.label || status || '未知'
}

function parseStatusTone(status) {
  return PARSE_STATUS[status]?.tone || 'neutral'
}

function showMessage(text, tone = 'info') {
  message.value = text
  messageTone.value = tone
}

function formatIssue(issue) {
  if (!issue) return ''
  let msg = typeof issue === 'string' ? issue : (issue.message || issue.title || '')
  
  const reqNoMatch = msg.match(/(REQ-\d+|API-\d+)/)
  if (reqNoMatch) {
    const no = reqNoMatch[0]
    const targetItem = requirementItems.value.find(item => item.requirement_no === no)
    if (targetItem) {
      let title = targetItem.title || targetItem.content?.substring(0, 15) || '未命名需求点'
      title = String(title).replace(/^[#\s|:-]+/, '').trim()
      msg = msg.replace(no, `《${title}》 (${no})`)
    }
  }
  return msg
}

function selectIssue(index) {
  selectedIssueIndex.value = selectedIssueIndex.value === index ? null : index
  if (selectedIssueIndex.value !== null) {
    nextTick(() => {
      const no = selectedIssueRequirementNo.value
      if (no) {
        const el = document.getElementById(`req-card-${no}`)
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    })
  }
}

function activateIssue(index) {
  if (typeof index === 'number') {
    selectedIssueIndex.value = index
  }
  return selectedIssue.value
}

function isAiSummaryFailure(summary) {
  return typeof summary === 'string' && summary.trim().startsWith('[AI 调用失败]')
}

function issueTypeLabel(issue) {
  const type = typeof issue === 'string' ? '' : (issue?.type || issue?.issue_type)
  const labels = {
    missing: '信息缺失',
    conflict: '逻辑冲突',
    ambiguous: '待确认',
    runtime_error: '接口异常',
    待修改: '待修改',
    待确认: '待确认',
    待优化: '待优化',
    已修改: '已修改',
    已解决: '已解决',
    逻辑漏洞: '逻辑漏洞',
    格式问题: '格式问题',
    '误报 / 已忽略': '已忽略',
  }
  return labels[type] || '待优化'
}

function issueSeverityLabel(issue) {
  if (!issue || typeof issue === 'string') return '中'
  return issue.severity || (issue.blocking ? '阻断' : '中')
}

function issueDetailText(issue) {
  if (!issue || typeof issue === 'string') return ''
  const parts = []
  if (issue.status) parts.push(`状态：${issue.status}`)
  if (issue.source_location) parts.push(`位置：${issue.source_location}`)
  if (issue.impact_scope) parts.push(`影响：${issue.impact_scope}`)
  if (issue.ignored_reason) parts.push(`忽略原因：${issue.ignored_reason}`)
  return parts.join(' · ')
}

function issueClass(issue) {
  if (typeof issue !== 'string' && issue?.blocking) {
    return { 'issue-critical': true }
  }
  const type = typeof issue === 'string' ? '' : issue?.type
  return {
    'issue-critical': ['missing', 'conflict', 'runtime_error'].includes(type),
  }
}

function documentTypeLabel(type) {
  const labels = {
    requirement_document: '需求文档',
    api_document: '接口文档',
    api_log: '线上接口 Log',
  }
  return labels[type] || type || '未知类型'
}

function historyDiffLabel(type) {
  const labels = {
    added: '新增需求',
    modified: '历史差异 / 需确认',
    deprecated: '删除或废弃风险',
    removed: '删除或废弃风险',
    ambiguous: '模糊项',
    conflict: '冲突项',
  }
  return labels[type] || type || '历史差异'
}

function historyDiffSummary(item) {
  const current = item.new || item.current || {}
  const previous = item.old || {}
  const currentTitle = current.title || current.content || ''
  const previousTitle = previous.title || previous.content || ''
  return [previousTitle && `历史：${previousTitle}`, currentTitle && `当前：${currentTitle}`].filter(Boolean).join('；') || JSON.stringify(item)
}

function categoryDescription(category) {
  return CATEGORY_DESCRIPTIONS[category] || '项目自定义分类；用于筛选、关联上下文和后续解析策略扩展。'
}

function formatRequirementItems(items) {
  return items.map((item) => {
    const excerpt = item.source_text ? `\n  依据：${item.source_text}` : ''
    return `- ${item.requirement_no || ''} ${item.title}: ${item.content || ''}${excerpt}`
  }).join('\n')
}

function requirementItemTitle(item) {
  const no = item.requirement_no ? `${item.requirement_no} · ` : ''
  return `${no}${item.title || '未命名需求点'}`
}

function requirementTypeLabel(type) {
  const labels = {
    requirement: '需求',
    new_feature: '新增功能',
    rule_change: '业务规则',
    risk: '风险点',
    acceptance: '验收点',
    acceptance_point: '验收点',
    api: '接口',
    rule: '规则',
  }
  return labels[type] || type || '需求'
}

function syncParsePayload(document) {
  parseIssues.value = []
  requirementItems.value = []
  parsePayload.value = null
  selectedIssueIndex.value = null
  if (!document?.parse_result) return
  try {
    const payload = typeof document.parse_result === 'string'
      ? JSON.parse(document.parse_result)
      : document.parse_result
    parsePayload.value = payload
    parseIssues.value = payload.issues || []
    selectedIssueIndex.value = parseIssues.value.length ? 0 : null
  } catch {
    parseIssues.value = []
    parsePayload.value = null
    selectedIssueIndex.value = null
  }
}

async function loadTree() {
  try {
    const response = await fetchRequirementTree()
    treeItems.value = response.items || []
  } catch (error) {
    showMessage(`加载需求树失败：${error.message}`, 'danger')
    treeItems.value = []
  }
}

async function loadCategories() {
  try {
    const response = await fetchRequirementCategories()
    categories.value = response.items || []
  } catch {
    categories.value = []
  }
}

async function loadIssueWorkbench(documentId) {
  try {
    const [issuesResponse, revisionsResponse] = await Promise.all([
      fetchRequirementIssues(documentId),
      fetchRequirementRevisions(documentId),
    ])
    parseIssues.value = issuesResponse.items || []
    requirementRevisions.value = revisionsResponse.items || []
    selectedIssueIndex.value = parseIssues.value.length ? 0 : null
  } catch {
    parseIssues.value = []
    requirementRevisions.value = []
    selectedIssueIndex.value = null
  }
}

async function loadDocuments() {
  loading.value = true
  try {
    if (showTrash.value) {
      const [deleted, archived] = await Promise.all([
        fetchTrashDocuments('deleted'),
        fetchTrashDocuments('archived'),
      ])
      documents.value = [...(deleted.items || []), ...(archived.items || [])]
    } else {
      const params = new URLSearchParams()
      if (keyword.value) params.set('keyword', keyword.value)
      if (categoryFilter.value) params.set('category', categoryFilter.value)
      if (selectedTreeNodeId.value) params.set('tree_node_id', String(selectedTreeNodeId.value))
      const response = await fetchRequirementDocuments(params)
      documents.value = response.items || []
    }
    if (selectedId.value && !documents.value.some((doc) => doc.id === selectedId.value)) {
      selectedId.value = null
      selectedDocument.value = null
    }
    if (!selectedId.value && documents.value[0]) {
      await selectDocument(documents.value[0].id)
    }
  } catch (error) {
    showMessage(`加载需求文档失败：${error.message}`, 'danger')
  } finally {
    loading.value = false
  }
}

async function selectTreeNode(nodeId) {
  if (showTrash.value) return
  selectedTreeNodeId.value = nodeId
  await loadDocuments()
}

async function selectDocument(documentId) {
  selectedId.value = documentId
  analysis.value = null
  parsePayload.value = null
  requirementItems.value = []
  requirementRevisions.value = []
  documentRelations.value = null
  try {
    selectedDocument.value = await fetchRequirementDocumentDetail(documentId)
    mountNodeId.value = selectedDocument.value?.tree_node_id || null
    selectedCategory.value = selectedDocument.value?.category || '未分类'
    treePathLabel.value = ''
    if (!showTrash.value) {
      try {
        const pathResponse = await fetchDocumentTreePath(documentId)
        treePathLabel.value = pathResponse.path_label || ''
      } catch {
        treePathLabel.value = ''
      }
      try {
        documentRelations.value = await fetchDocumentRelations(documentId)
      } catch {
        documentRelations.value = null
      }
    }
    syncParsePayload(selectedDocument.value)
    await loadIssueWorkbench(documentId)
    if (
      selectedDocument.value.parse_status === 'stored'
      || selectedDocument.value.parse_status === 'pending_review'
      || selectedDocument.value.parse_status === 'check_failed'
    ) {
      try {
        const itemsResponse = await fetchRequirementItems(documentId)
        requirementItems.value = itemsResponse.items || []
      } catch {
        requirementItems.value = []
      }
    }
    if (selectedDocument.value.file_type === 'md' && !requirementItems.value.length) {
      try {
        analysis.value = await fetchRequirementDocumentAnalysis(documentId)
      } catch {
        analysis.value = null
      }
    }
  } catch (error) {
    showMessage(`加载文档详情失败：${error.message}`, 'danger')
  }
}

function openIssueEditor(mode, index = null) {
  const issue = activateIssue(index)
  if (!issue?.id) return
  issueEditorMode.value = mode
  issueForm.revised_excerpt = issue.source_excerpt || ''
  issueForm.reason = ''
  issueForm.risk_accepted = false
  issueEditorVisible.value = true
}

async function submitIssueEditor() {
  if (!selectedIssueId.value || !selectedId.value) return
  if (issueEditorMode.value === 'modify' && !issueForm.revised_excerpt.trim()) {
    showMessage('修订内容不能为空', 'danger')
    return
  }
  if (issueEditorMode.value === 'ignore' && issueForm.reason.trim().length < 10) {
    showMessage('忽略原因不能少于 10 字', 'danger')
    return
  }
  actionLoading.value = true
  try {
    if (issueEditorMode.value === 'modify') {
      const result = await modifyRequirementIssue(selectedIssueId.value, {
        revised_excerpt: issueForm.revised_excerpt,
        reason: issueForm.reason,
        operator: 'frontend',
      })
      if (result.document?.parse_status === 'pending_review') {
        showMessage('问题项已修改并重新检查，可继续确认入库', 'success')
      } else {
        showMessage('问题项已修改并重新检查，仍有待处理问题', 'warning')
      }
    } else {
      await ignoreRequirementIssue(selectedIssueId.value, {
        reason: issueForm.reason,
        operator: 'frontend',
        risk_accepted: issueForm.risk_accepted,
      })
      showMessage('问题项已忽略并留痕', 'success')
    }
    issueEditorVisible.value = false
    await selectDocument(selectedId.value)
    await loadDocuments()
  } catch (error) {
    showMessage(`处理问题项失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitAcceptSuggestion(index = null) {
  activateIssue(index)
  if (!selectedIssueId.value || !selectedId.value) return
  actionLoading.value = true
  try {
    const result = await acceptRequirementIssueSuggestion(selectedIssueId.value, {
      reason: '前端采纳 AI 修改建议',
      operator: 'frontend',
    })
    if (result.document?.parse_status === 'pending_review') {
      showMessage('已采纳 AI 建议并重新检查，可继续确认入库', 'success')
    } else {
      showMessage('已采纳 AI 建议并重新检查，仍有待处理问题', 'warning')
    }
    await selectDocument(selectedId.value)
    await loadDocuments()
  } catch (error) {
    showMessage(`采纳 AI 建议失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitManualReview(index = null) {
  activateIssue(index)
  if (!selectedIssueId.value || !selectedId.value) return
  actionLoading.value = true
  try {
    await manualReviewRequirementIssue(selectedIssueId.value, {
      reason: '前端转人工确认，等待产品或研发复核',
      operator: 'frontend',
    })
    showMessage('问题项已转人工确认', 'success')
    await selectDocument(selectedId.value)
  } catch (error) {
    showMessage(`转人工确认失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitResolveIssue(index = null) {
  activateIssue(index)
  if (!selectedIssueId.value || !selectedId.value) return
  actionLoading.value = true
  try {
    await resolveRequirementIssue(selectedIssueId.value, {
      reason: '前端确认问题已解决',
      operator: 'frontend',
    })
    showMessage('问题项已标记为解决', 'success')
    await selectDocument(selectedId.value)
    await loadDocuments()
  } catch (error) {
    showMessage(`标记解决失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitIssueRecheck(index = null) {
  activateIssue(index)
  if (!selectedIssueId.value || !selectedId.value) return
  actionLoading.value = true
  try {
    await recheckRequirementIssue(selectedIssueId.value, { operator: 'frontend' })
    showMessage('问题项已重新检查', 'success')
    await selectDocument(selectedId.value)
    await loadDocuments()
  } catch (error) {
    showMessage(`重新检查问题项失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitRecheck() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    await recheckRequirementDocument(selectedId.value, { operator: 'frontend' })
    showMessage('文档已重新检查', 'success')
    await selectDocument(selectedId.value)
    await loadDocuments()
  } catch (error) {
    showMessage(`重新检查失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

function downloadSelectedDocument() {
  if (!selectedId.value) return
  window.open(`${API_BASE}/api/requirements/documents/${selectedId.value}/download`, '_blank', 'noopener')
}

function onFileChange(event) {
  uploadForm.file = event.target.files?.[0] || null
}

function openUploadModal() {
  uploadForm.tree_node_id = selectedTreeNodeId.value || null
  uploadVisible.value = true
}

async function submitUpload() {
  if (!uploadForm.file) {
    showMessage('请选择要上传的文件', 'danger')
    return
  }
  uploading.value = true
  try {
    const payload = {
      file: uploadForm.file,
      title: uploadForm.title,
      category: uploadForm.category,
      module: uploadForm.module,
      created_by: 'frontend',
    }
    if (uploadForm.tree_node_id) {
      payload.tree_node_id = uploadForm.tree_node_id
    }
    const uploaded = await uploadRequirementDocument(payload)
    uploadVisible.value = false
    uploadForm.title = ''
    uploadForm.module = ''
    uploadForm.tree_node_id = null
    uploadForm.file = null
    showMessage('文档上传成功', 'success')
    await loadDocuments()
    if (uploaded?.id) await selectDocument(uploaded.id)
  } catch (error) {
    showMessage(`上传失败：${error.message}`, 'danger')
  } finally {
    uploading.value = false
  }
}

function openTreeEditor(mode) {
  treeEditorMode.value = mode
  if (mode === 'edit') {
    const node = treeNodeMap.value[selectedTreeNodeId.value]
    treeForm.name = node?.name || ''
    treeForm.node_type = node?.node_type || 'domain'
  } else if (mode === 'create-child') {
    treeForm.name = ''
    treeForm.node_type = 'module'
  } else {
    treeForm.name = ''
    treeForm.node_type = 'domain'
  }
  treeEditorVisible.value = true
}

async function submitTreeEditor() {
  if (!treeForm.name.trim()) {
    showMessage('节点名称不能为空', 'danger')
    return
  }
  try {
    if (treeEditorMode.value === 'edit') {
      await updateTreeNode(selectedTreeNodeId.value, {
        name: treeForm.name.trim(),
        node_type: treeForm.node_type,
      })
      showMessage('节点已更新', 'success')
    } else {
      const payload = {
        name: treeForm.name.trim(),
        node_type: treeForm.node_type,
        parent_id: treeEditorMode.value === 'create-child' ? selectedTreeNodeId.value : null,
      }
      const created = await createTreeNode(payload)
      showMessage('节点已创建', 'success')
      selectedTreeNodeId.value = created.id
    }
    treeEditorVisible.value = false
    await loadTree()
    await loadDocuments()
  } catch (error) {
    showMessage(`保存节点失败：${error.message}`, 'danger')
  }
}

async function removeTreeNode() {
  if (!selectedTreeNodeId.value) return
  if (!window.confirm('确认删除该节点？需先移除子节点与挂载文档。')) return
  try {
    await deleteTreeNode(selectedTreeNodeId.value)
    selectedTreeNodeId.value = null
    showMessage('节点已删除', 'success')
    await loadTree()
    await loadDocuments()
  } catch (error) {
    showMessage(`删除节点失败：${error.message}`, 'danger')
  }
}

async function submitMountFromDetail() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    selectedDocument.value = await mountDocument(selectedId.value, mountNodeId.value)
    showMessage(mountNodeId.value ? '文档已挂载到关系树节点' : '已取消挂载', 'success')
    await loadDocuments()
  } catch (error) {
    mountNodeId.value = selectedDocument.value?.tree_node_id || null
    showMessage(`挂载失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitCategoryChangeFromDetail() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    const updated = await updateDocumentMeta(selectedId.value, {
      category: selectedCategory.value,
    })
    selectedDocument.value = updated
    selectedCategory.value = updated.category || '未分类'
    syncParsePayload(updated)
    showMessage('业务分类已成功更新，可重新触发解析以运行对应 Skill', 'success')
    await loadDocuments()
  } catch (error) {
    selectedCategory.value = selectedDocument.value?.category || '未分类'
    showMessage(`更新分类失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

function openMoveDialog() {
  if (!selectedDocument.value) return
  moveForm.from_tree_node_id = selectedDocument.value.tree_node_id || null
  moveForm.target_tree_node_id = selectedDocument.value.tree_node_id || null
  moveDialogVisible.value = true
}

async function submitMoveDocument() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    selectedDocument.value = await moveDocument(selectedId.value, {
      from_tree_node_id: moveForm.from_tree_node_id,
      target_tree_node_id: moveForm.target_tree_node_id,
    })
    mountNodeId.value = selectedDocument.value?.tree_node_id || null
    moveDialogVisible.value = false
    showMessage(moveForm.target_tree_node_id ? '文档已移动到目标节点' : '文档已取消挂载', 'success')
    await loadTree()
    await loadDocuments()
    await selectDocument(selectedId.value)
  } catch (error) {
    showMessage(`移动节点失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitGenerateCases() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    const result = await generateCasesFromDocument({
      document_id: selectedId.value,
      target_platform: 'functional',
      case_count: 3,
    })
    const count = result?.draft_count ?? result?.cases?.length ?? 0
    showMessage(count ? `已生成 ${count} 条 case 草稿，请到 Case 中心确认` : 'case 草稿已生成', 'success')
  } catch (error) {
    showMessage(`生成 case 草稿失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitParse() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    const result = await parseDocument(selectedId.value)
    selectedDocument.value = result.document
    parseIssues.value = result.issues || []
    requirementItems.value = result.requirement_points || []
    selectedIssueIndex.value = parseIssues.value.length ? 0 : null
    showMessage(parseIssues.value.length ? '解析完成，但存在检查问题' : '解析完成，待人工确认入库', parseIssues.value.length ? 'danger' : 'success')
    await loadDocuments()
  } catch (error) {
    showMessage(`解析失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitConfirm() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    selectedDocument.value = await confirmDocument(selectedId.value)
    showMessage('文档已确认入库，可作为 case 生成依据', 'success')
    await loadDocuments()
    await selectDocument(selectedId.value)
  } catch (error) {
    showMessage(`确认入库失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function confirmWithImpact(actionLabel) {
  if (!selectedId.value) return false
  try {
    const impact = await fetchDocumentImpact(selectedId.value)
    const message = [
      `确认${actionLabel}？`,
      `关联需求点：${impact.requirement_item_count} 条`,
      `关联 case：${impact.case_count} 条`,
      `知识库片段：${impact.knowledge_fragment_count} 条`,
      `变更记录：${impact.change_record_count ?? 0} 条`,
    ].join('\n')
    return window.confirm(message)
  } catch {
    return window.confirm(`确认${actionLabel}？`)
  }
}

async function submitArchive() {
  if (!selectedId.value || !(await confirmWithImpact('归档该文档'))) return
  actionLoading.value = true
  try {
    await archiveDocument(selectedId.value)
    selectedId.value = null
    selectedDocument.value = null
    showMessage('文档已归档', 'success')
    await loadDocuments()
  } catch (error) {
    showMessage(`归档失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitSoftDelete() {
  if (!selectedId.value || !(await confirmWithImpact('移入回收站'))) return
  actionLoading.value = true
  try {
    await softDeleteDocument(selectedId.value)
    selectedId.value = null
    selectedDocument.value = null
    showMessage('文档已移入回收站', 'success')
    await loadDocuments()
  } catch (error) {
    showMessage(`删除失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function submitRestore() {
  if (!selectedId.value) return
  actionLoading.value = true
  try {
    await restoreDocument(selectedId.value)
    showMessage('文档已恢复', 'success')
    showTrash.value = false
    await loadTree()
    await loadDocuments()
    await selectDocument(selectedId.value)
  } catch (error) {
    showMessage(`恢复失败：${error.message}`, 'danger')
  } finally {
    actionLoading.value = false
  }
}

async function toggleTrashView() {
  showTrash.value = !showTrash.value
  selectedId.value = null
  selectedDocument.value = null
  await loadDocuments()
}

onMounted(async () => {
  await Promise.all([loadTree(), loadCategories()])
  await loadDocuments()
})
</script>

<style scoped>
.issue-card-list {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.issue-card {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 16px;
  background: var(--surface-color, #fff);
  cursor: pointer;
}

.issue-card.selected {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.issue-card.issue-critical {
  border-color: #ef4444;
}

.issue-card-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  gap: 12px;
}

.issue-card-header .chip-row {
  grid-column: 2;
  grid-row: 1;
  justify-content: flex-end;
}

.issue-card-header strong {
  grid-column: 1;
  grid-row: 1;
  line-height: 1.5;
}

.issue-card-body {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.issue-card-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(120px, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.issue-tag.danger {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 1400px) {
  .issue-card-header {
    grid-template-columns: 1fr;
  }

  .issue-card-header .chip-row,
  .issue-card-header strong {
    grid-column: auto;
    grid-row: auto;
    justify-content: flex-start;
  }

  .issue-card-actions {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
