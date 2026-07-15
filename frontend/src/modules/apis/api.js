import { request } from '../../shared/api/http'

export async function fetchApis() {
  return request('/api/apis')
}
