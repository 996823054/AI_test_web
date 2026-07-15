import { request } from '../../shared/api/http'

export async function fetchDashboard() {
  return request('/api/reports/dashboard')
}
