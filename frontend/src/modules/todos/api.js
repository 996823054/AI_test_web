import { request } from '../../shared/api/http'

export async function fetchTodos() {
  return request('/api/todos')
}
