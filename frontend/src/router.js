import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from './layouts/AdminLayout.vue'
import EmployeeLayout from './layouts/EmployeeLayout.vue'
import AdminIngestPage from './views/AdminIngestPage.vue'
import EmployeeChatPage from './views/EmployeeChatPage.vue'
import AdminCompaniesPage from './views/AdminCompaniesPage.vue'
import LoginPage from './views/LoginPage.vue'
import SignupPage from './views/SignupPage.vue'
import { authState } from './authStore'
import HomePage from './views/HomePage.vue'
import CompanyUsersPage from './views/CompanyUsersPage.vue'
import NotAllowedPage from './views/NotAllowedPage.vue'
import FirstLogin from './views/FirstLoginPage.vue'
import OrganizationPage from './views/OrganizationsAdminPage.vue'

const adminRoles = [
  'vendor',
  'group_admin',
  'group_exe',
  'group_hr',
  'group_finance',
  'group_operation',
  'group_production',
  'group_marketing',
  'group_legal',
  'sub_admin',
  'sub_md',
  'sub_hr',
  'sub_finance',
  'sub_operations',
  'sub_legal',
  'group_gmd',
  'employee',
]

// Routes
const routes = [
  // Public home
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },

  // Auth
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/signup', name: 'signup', component: SignupPage },
  { path: '/auth', redirect: '/login' },

  // Admin area (restricted to adminRoles)
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      roles: adminRoles,
    },
    children: [
      {
        path: 'ingest',
        name: 'admin-ingest',
        component: AdminIngestPage,
      },
      {
        path: 'companies',
        name: 'admin-companies',
        component: AdminCompaniesPage,
      },
      {
        path: 'users',
        name: 'company-users',
        component: CompanyUsersPage,
        meta: { requiresAuth: true, roles: adminRoles },
      },
    ],
  },

  // Employee/chat area (any adminRoles user)
  {
    path: '/chat',
    component: EmployeeLayout,
    meta: {
      requiresAuth: true,
      roles: adminRoles,
    },
    children: [
      {
        path: '',
        name: 'employee-chat',
        component: EmployeeChatPage,
      },
    ],
  },

  // First login (any authenticated user)
  {
    path: '/first-login',
    name: 'first-login',
    component: FirstLogin,
    meta: { requiresAuth: true },
  },

  // Not allowed (public, no auth/role requirements)
  {
    path: '/not-allowed',
    name: 'not-allowed',
    component: NotAllowedPage,
    meta: {},
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Global auth + role guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!authState.accessToken
  const role = authState.user?.role

  // Auth check
  if (to.matched.some(r => r.meta.requiresAuth) && !isAuthenticated) {
    if (to.name === 'login') return next()
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Role check
  const requiredRoles = to.matched
    .filter(r => Array.isArray(r.meta?.roles) && r.meta.roles.length)
    .flatMap(r => r.meta.roles)

  if (requiredRoles.length && role && !requiredRoles.includes(role)) {
    if (to.name === 'not-allowed') return next()
    return next({ name: 'not-allowed' })
  }

  next()
})

export default router
