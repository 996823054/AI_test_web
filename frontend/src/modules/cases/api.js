import { request } from '../../shared/api/http'

function buildCasesQuery(params) {
  if (!params) return ''
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function fetchCases(params) {
  return request(`/api/cases${buildCasesQuery(params)}`)
}

export function fetchCaseDetail(caseId) {
  return request(`/api/cases/${caseId}`)
}

export function fetchCaseVersions(caseId) {
  return request(`/api/cases/${caseId}/versions`)
}

export function createCase(payload) {
  return request('/api/cases/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateCase(caseId, payload) {
  return request(`/api/cases/${caseId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deprecateCase(caseId, payload = {}) {
  return request(`/api/cases/${caseId}/deprecate`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function copyCase(caseId, payload = {}) {
  return request(`/api/cases/${caseId}/copy`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchCaseDrafts(params) {
  return request(`/api/cases/drafts${buildCasesQuery(params)}`)
}

export function acceptCaseDraft(draftId, confirmedBy = 'frontend', overrides = null) {
  return request(`/api/cases/drafts/${draftId}/accept`, {
    method: 'POST',
    body: JSON.stringify({ confirmed_by: confirmedBy, overrides }),
  })
}

export function rejectCaseDraft(draftId, payload = {}) {
  return request(`/api/cases/drafts/${draftId}/reject`, {
    method: 'POST',
    body: JSON.stringify({ ...payload, rejected_by: payload.rejected_by || 'frontend' }),
  })
}

export function deleteCase(caseId) {
  const id = Number(caseId)
  if (!Number.isInteger(id) || id <= 0) {
    return Promise.reject(new Error('无效的 case ID'))
  }
  return request(`/api/cases/${id}`, {
    method: 'DELETE',
  })
}
