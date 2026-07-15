import { request } from '../../shared/api/http'

export async function fetchPhoenixEvaluators() {
  return request('/api/ai/phoenix-evaluators')
}
