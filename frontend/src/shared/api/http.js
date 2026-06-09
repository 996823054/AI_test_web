export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers || {}),
  }

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    })
  } catch (error) {
    throw new Error(`无法连接后端服务（${API_BASE}），请确认服务已启动并且端口可访问`)
  }

  if (!response.ok) {
    const message = await response.text()
    throw new Error(formatErrorMessage(message) || `Request failed: ${response.status}`)
  }

  const text = await response.text()
  return text ? JSON.parse(text) : null
}

export function formatErrorMessage(message) {
  if (!message) return ''
  try {
    const payload = JSON.parse(message)
    const detail = payload.detail ?? payload
    if (typeof detail === 'string') return detail
    if (detail?.message) {
      const issueSummary = Array.isArray(detail.blocking_issues) && detail.blocking_issues.length
        ? `：${detail.blocking_issues.map((issue) => issue.title || issue.message || `问题项 #${issue.id}`).join('、')}`
        : ''
      return `${detail.message}${issueSummary}`
    }
    return JSON.stringify(detail)
  } catch {
    return message
  }
}

export async function fetchHealth() {
  return request('/health')
}
