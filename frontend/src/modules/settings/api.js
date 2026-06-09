import { request } from '../../shared/api/http'

export function fetchSettings() {
  return request('/api/settings')
}

export function saveSettings(payload) {
  return request('/api/settings', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function resetSettings() {
  return request('/api/settings/reset', { method: 'POST' })
}

export function fetchAiModels() {
  return request('/api/settings/ai-models')
}

export function saveAiModel(payload) {
  return request('/api/settings/ai-models', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteAiModel(modelId) {
  return request(`/api/settings/ai-models/${encodeURIComponent(modelId)}`, {
    method: 'DELETE',
  })
}

export function setDefaultAiModel(modelId) {
  return request(`/api/settings/ai-models/${encodeURIComponent(modelId)}/default`, {
    method: 'POST',
  })
}

export function checkAiModel(modelId, payload = {}) {
  return request(`/api/settings/ai-models/${encodeURIComponent(modelId)}/check`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function checkTempAiModel(payload) {
  return request('/api/settings/ai-models/check', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchAiProviders() {
  return request('/api/settings/ai-providers')
}
