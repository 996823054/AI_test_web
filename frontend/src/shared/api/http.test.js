import { afterEach, describe, expect, it, vi } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { formatErrorMessage } from './http.js'
import {
  acceptRequirementIssueSuggestion,
  fetchDocumentRelations,
  recheckRequirementIssue,
} from '../../modules/requirements/api.js'
import {
  acceptCaseDraft,
  copyCase,
  deprecateCase,
} from '../../modules/cases/api.js'

function mockJsonResponse(payload = {}) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    text: () => Promise.resolve(JSON.stringify(payload)),
  })
}

describe('API request helpers', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('formats structured blocking issue errors for display', () => {
    const message = formatErrorMessage(JSON.stringify({
      detail: {
        message: '文档存在未解决的阻断级问题',
        blocking_issues: [{ id: 1, title: '缺少验收标准' }],
      },
    }))

    expect(message).toContain('文档存在未解决的阻断级问题')
    expect(message).toContain('缺少验收标准')
  })

  it('calls requirement issue actions and relations endpoints', async () => {
    mockJsonResponse({ ok: true })

    await recheckRequirementIssue(7, { operator: 'tester' })
    await acceptRequirementIssueSuggestion(8, { operator: 'tester' })
    await fetchDocumentRelations(9)

    expect(global.fetch.mock.calls[0][0]).toContain('/api/requirements/issues/7/recheck')
    expect(global.fetch.mock.calls[1][0]).toContain('/api/requirements/issues/8/accept-suggestion')
    expect(global.fetch.mock.calls[2][0]).toContain('/api/requirements/documents/9/relations')
  })

  it('calls case governance endpoints with expected methods', async () => {
    mockJsonResponse({ ok: true })

    await acceptCaseDraft(3, { confirmed_by: 'tester' })
    await copyCase(4, { copied_by: 'tester' })
    await deprecateCase(5, { category: 'OTHER', reason: '这是一个足够长的废弃原因' })

    expect(global.fetch.mock.calls[0][0]).toContain('/api/cases/drafts/3/accept')
    expect(global.fetch.mock.calls[0][1].method).toBe('POST')
    expect(global.fetch.mock.calls[1][0]).toContain('/api/cases/4/copy')
    expect(global.fetch.mock.calls[2][0]).toContain('/api/cases/5/deprecate')
  })
})

describe('Requirements issue workbench layout', () => {
  it('renders each requirement issue as an independent card with its own actions', () => {
    const component = readFileSync(
      resolve(process.cwd(), 'src/modules/requirements/pages/RequirementsPage.vue'),
      'utf-8',
    )

    expect(component).toContain('class="issue-card-actions"')
    expect(component).toContain('v-for="(issue, index) in parseIssues"')
    expect(component).toContain('@click.stop="openIssueEditor(\'modify\', index)"')
    expect(component).not.toContain('<div v-if="selectedIssue" class="toolbar">')
  })

  it('tells users to handle need-review requirement points in issue cards', () => {
    const component = readFileSync(
      resolve(process.cwd(), 'src/modules/requirements/pages/RequirementsPage.vue'),
      'utf-8',
    )

    expect(component).toContain('需复核项已同步到上方问题项卡片')
  })

  it('keeps the issue workbench full width like the AI summary card', () => {
    const styles = readFileSync(
      resolve(process.cwd(), 'src/styles/components.css'),
      'utf-8',
    )

    expect(styles).toContain('.issue-workbench')
    expect(styles).toContain('grid-template-columns: minmax(0, 1fr);')
    expect(styles).not.toContain('grid-template-columns: minmax(0, 1.25fr) minmax(220px, 0.75fr);')
  })

  it('uses backend rechecked document result after issue text revision actions', () => {
    const component = readFileSync(
      resolve(process.cwd(), 'src/modules/requirements/pages/RequirementsPage.vue'),
      'utf-8',
    )

    expect(component).toMatch(/const result = await modifyRequirementIssue[\s\S]*result\.document\?\.parse_status === 'pending_review'/)
    expect(component).toMatch(/const result = await acceptRequirementIssueSuggestion[\s\S]*result\.document\?\.parse_status === 'pending_review'/)
  })

  it('shows recheck outcome based on document parse status after revision actions', () => {
    const component = readFileSync(
      resolve(process.cwd(), 'src/modules/requirements/pages/RequirementsPage.vue'),
      'utf-8',
    )

    expect(component).toContain("result.document?.parse_status === 'pending_review'")
    expect(component).toContain('仍有待处理问题')
  })

  it('loads requirement items while document is check_failed for issue linkage', () => {
    const component = readFileSync(
      resolve(process.cwd(), 'src/modules/requirements/pages/RequirementsPage.vue'),
      'utf-8',
    )

    expect(component).toContain("selectedDocument.value.parse_status === 'check_failed'")
  })
})
