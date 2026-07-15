import { request } from '../../shared/api/http'

export async function fetchBatches() {
  return request('/api/executions/batches')
}
