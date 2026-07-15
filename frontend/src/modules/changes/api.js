import { request } from '../../shared/api/http'

export async function fetchChangelog() {
  return request('/api/changelog')
}
