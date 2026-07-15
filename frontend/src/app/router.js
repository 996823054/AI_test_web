import { createRouter, createWebHistory } from 'vue-router'
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

const routes = [
  {
    path: '/',
    component: AppShell,
    redirect: '/overview',
    children: [
      { path: 'overview', name: 'overview', component: OverviewPage },
      { path: 'requirements', name: 'requirements', component: RequirementsPage },
      { path: 'cases', name: 'cases', component: CasesPage },
      { path: 'apis', name: 'apis', component: ApisPage },
      { path: 'executions', name: 'executions', component: ExecutionsPage },
      { path: 'reports', name: 'reports', component: ReportsPage },
      { path: 'mobile', name: 'mobile', component: MobilePage },
      { path: 'ai', name: 'ai', component: AiPage },
      { path: 'changes', name: 'changes', component: ChangesPage },
      { path: 'todos', name: 'todos', component: TodosPage },
      { path: 'settings', name: 'settings', component: SettingsPage },
    ],
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
