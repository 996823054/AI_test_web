import { request } from '../../shared/api/http'

export function fetchRequirementDocuments(params) {
  const query = params ? `?${params.toString()}` : ''
  return request(`/api/ai/documents${query}`)
}

export function fetchRequirementCategories() {
  return request('/api/ai/documents/categories')
}

export function fetchRequirementDocumentDetail(documentId) {
  return request(`/api/ai/documents/${documentId}`)
}

export function fetchRequirementDocumentAnalysis(documentId) {
  return request(`/api/ai/documents/${documentId}/analysis`)
}

export function fetchRequirementIssues(documentId, status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/api/requirements/documents/${documentId}/issues${query}`)
}

export function fetchRequirementRevisions(documentId) {
  return request(`/api/requirements/documents/${documentId}/revisions`)
}

export function modifyRequirementIssue(issueId, payload) {
  return request(`/api/requirements/issues/${issueId}/modify`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function acceptRequirementIssueSuggestion(issueId, payload = {}) {
  return request(`/api/requirements/issues/${issueId}/accept-suggestion`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function ignoreRequirementIssue(issueId, payload) {
  return request(`/api/requirements/issues/${issueId}/ignore`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function manualReviewRequirementIssue(issueId, payload = {}) {
  return request(`/api/requirements/issues/${issueId}/manual-review`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function resolveRequirementIssue(issueId, payload = {}) {
  return request(`/api/requirements/issues/${issueId}/resolve`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function recheckRequirementIssue(issueId, payload = {}) {
  return request(`/api/requirements/issues/${issueId}/recheck`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function recheckRequirementDocument(documentId, payload = {}) {
  return request(`/api/requirements/documents/${documentId}/recheck`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function uploadRequirementDocument(payload) {
  const form = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null) form.append(key, value)
  })
  return request('/api/ai/documents/upload', {
    method: 'POST',
    body: form,
  })
}

export function fetchRequirementTree() {
  return request('/api/requirements/tree')
}

export function createTreeNode(payload) {
  return request('/api/requirements/tree', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateTreeNode(nodeId, payload) {
  return request(`/api/requirements/tree/${nodeId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteTreeNode(nodeId) {
  return request(`/api/requirements/tree/${nodeId}`, {
    method: 'DELETE',
  })
}

export function mountDocument(documentId, treeNodeId) {
  return request(`/api/requirements/documents/${documentId}/mount`, {
    method: 'POST',
    body: JSON.stringify({ tree_node_id: treeNodeId ?? null }),
  })
}

export function moveDocument(documentId, payload) {
  return request(`/api/requirements/documents/${documentId}/move`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function generateCasesFromDocument(payload) {
  return request('/api/ai/generate-cases-from-document', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function parseDocument(documentId) {
  return request(`/api/requirements/documents/${documentId}/parse`, {
    method: 'POST',
  })
}

export function confirmDocument(documentId) {
  return request(`/api/requirements/documents/${documentId}/confirm`, {
    method: 'POST',
  })
}

export function fetchRequirementItems(documentId) {
  return request(`/api/requirements/documents/${documentId}/items`)
}

export function archiveDocument(documentId) {
  return request(`/api/requirements/documents/${documentId}/archive`, {
    method: 'POST',
  })
}

export function softDeleteDocument(documentId) {
  return request(`/api/requirements/documents/${documentId}/delete`, {
    method: 'POST',
  })
}

export function restoreDocument(documentId) {
  return request(`/api/requirements/documents/${documentId}/restore`, {
    method: 'POST',
  })
}

export function fetchTrashDocuments(status = 'deleted') {
  return request(`/api/requirements/documents/trash?status=${status}`)
}

export function fetchDocumentImpact(documentId) {
  return request(`/api/requirements/documents/${documentId}/impact`)
}

export function fetchDocumentRelations(documentId) {
  return request(`/api/requirements/documents/${documentId}/relations`)
}

export function fetchDocumentTreePath(documentId) {
  return request(`/api/requirements/documents/${documentId}/tree-path`)
}

export function updateDocumentMeta(documentId, payload) {
  return request(`/api/requirements/documents/${documentId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}
