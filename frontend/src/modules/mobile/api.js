import { request } from '../../shared/api/http'

export async function fetchMobileStatus() {
  return { status: 'scaffold', message: '移动端正式域骨架已建立' }
}
