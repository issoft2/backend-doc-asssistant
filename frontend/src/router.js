import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from './layouts/AdminLayout.vue'
import EmployeeLayout from './layouts/EmployeeLayout.vue'
import AdminIngestPage from './views/AdminIngestPage.vue'
import EmployeeChatPage from './views/EmployeeChatPage.vue'
import AdminCompaniesPage from './views/AdminCompaniesPage.vue'
import LoginPage from './views/LoginPage.vue'
import SignupPage from './views/SignupPage.vue'
import { authState } from './authStore'
import HomePage from './views/HomePage.vue'   // ⬅ add this
import CompanyUsersPage from './views/CompanyUsersPage.vue'


const routes = [

  {
    path: '/',
    name: 'home',
    component: HomePage,
  },

  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      roles: ['hr', 'executive', 'management', 'vendor'], // only these see admin layout
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
      },
    ],
  },

  { path: '/login', name: 'login', component: LoginPage },
  { path: '/signup', name: 'signup', component: SignupPage },

  {
    path: '/chat',
    component: EmployeeLayout,
    meta: {
      requiresAuth: true,
      roles: ['employee', 'hr', 'executive', 'management', 'vendor'], // everyone logged in
    },
    children: [
      {
        path: '',
        name: 'employee-chat',
        component: EmployeeChatPage,
      },
    ],
  },

  { path: '/auth', redirect: '/login' },

]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// global auth + role guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!authState.accessToken
  const role = authState.user?.role

  if (to.matched.some(r => r.meta.requiresAuth) && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  const requiredRoles = to.matched
    .filter(r => r.meta && r.meta.roles)
    .flatMap(r => r.meta.roles || [])

  if (requiredRoles.length && role && !requiredRoles.includes(role)) {
    // employee trying to hit /admin → send to chat
    return next({ name: 'employee-chat' })
  }

  next()
})

export default router
