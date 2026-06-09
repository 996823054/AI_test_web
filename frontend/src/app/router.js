import { createRouter, createWebHistory } from 'vue-router'
import AppShell from './layout/AppShell.vue'
import OverviewPage from '../modules/overview/pages/OverviewPage.vue'
import RequirementsPage from '../modules/requirements/pages/RequirementsPage.vue'
import CasesPage from '../modules/cases/pages/CasesPage.vue'
import SettingsPage from '../modules/settings/pages/SettingsPage.vue'

const routes = [
  {
    path: '/',
    component: AppShell,
    redirect: '/overview',
    children: [
      { path: 'overview', name: 'overview', component: OverviewPage },
      { path: 'requirements', name: 'requirements', component: RequirementsPage },
      { path: 'cases', name: 'cases', component: CasesPage },
      { path: 'settings', name: 'settings', component: SettingsPage },
    ],
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
