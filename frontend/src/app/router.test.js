import { describe, expect, it } from 'vitest'
import router from './router'

describe('platform module routes', () => {
  it('registers PRD-aligned module paths', () => {
    const paths = router.getRoutes().map((route) => route.path)
    for (const expected of [
      '/overview',
      '/requirements',
      '/cases',
      '/apis',
      '/executions',
      '/reports',
      '/mobile',
      '/ai',
      '/changes',
      '/todos',
      '/settings',
    ]) {
      expect(paths).toContain(expected)
    }
  })
})
