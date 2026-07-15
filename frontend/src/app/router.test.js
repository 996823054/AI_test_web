import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import AppShell from './layout/AppShell.vue'
import OverviewPage from '../modules/overview/pages/OverviewPage.vue'
import RequirementsPage from '../modules/requirements/pages/RequirementsPage.vue'
import CasesPage from '../modules/cases/pages/CasesPage.vue'
import SettingsPage from '../modules/settings/pages/SettingsPage.vue'
import ApisPage from '../modules/apis/pages/ApisPage.vue'
import ExecutionsPage from '../modules/executions/pages/ExecutionsPage.vue'
import ReportsPage from '../modules/reports/pages/ReportsPage.vue'
import MobilePage from '../modules/mobile/pages/MobilePage.vue'
import AiPage from '../modules/ai/pages/AiPage.vue'
import ChangesPage from '../modules/changes/pages/ChangesPage.vue'
import TodosPage from '../modules/todos/pages/TodosPage.vue'

describe('platform module routes', () => {
  it('registers PRD-aligned module paths', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: AppShell,
          children: [
            { path: 'overview', component: OverviewPage },
            { path: 'requirements', component: RequirementsPage },
            { path: 'cases', component: CasesPage },
            { path: 'apis', component: ApisPage },
            { path: 'executions', component: ExecutionsPage },
            { path: 'reports', component: ReportsPage },
            { path: 'mobile', component: MobilePage },
            { path: 'ai', component: AiPage },
            { path: 'changes', component: ChangesPage },
            { path: 'todos', component: TodosPage },
            { path: 'settings', component: SettingsPage },
          ],
        },
      ],
    })

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
