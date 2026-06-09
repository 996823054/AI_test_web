import { request, fetchHealth } from '../../shared/api/http'
import { fetchRequirementDocuments } from '../requirements/api'
import { fetchCases } from '../cases/api'

export { fetchHealth }

export async function fetchOverviewStats() {
  const [health, documents, cases] = await Promise.all([
    fetchHealth(),
    fetchRequirementDocuments().catch(() => ({ total: 0 })),
    fetchCases().catch(() => ({ total: 0 })),
  ])

  return {
    health,
    documentTotal: documents.total || 0,
    caseTotal: cases.total || 0,
  }
}
