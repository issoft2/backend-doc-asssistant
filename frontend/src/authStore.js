// authStore.js
import { reactive } from 'vue'
import router from './router'
import api from './api'

import { setAuthToken, login as apiLogin, me as apiMe } from './api'

export const authState = reactive({
  accessToken: localStorage.getItem('access_token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
})

export async function login({ email, password }) {
  const { data } = await apiLogin({ email, password })
  
  if (data.requires_tenant_selection) {
    // phase 1 only: no token, no /me, no redirect
    return data
  }

  // single-tenant case: token is already present
  const token = data.access_token
  if (!token) {
    throw new Error('No token returned from login')
  }

  authState.accessToken = token
  setAuthToken(token)

  const { data: user } = await apiMe()
  authState.user = user
  localStorage.setItem('user', JSON.stringify(user))

  if (['hr', 'executive', 'management'].includes(user.role)) {
    await router.push('/admin/companies')
  } else {
    await router.push('/chat')
  }

  return data
}

export async function loginToTenant({ email, tenant_id }) {
  const { data } = await api.post('/auth/login/tenant', {
    email,
    tenant_id,
  })

  const token = data.access_token
  if (!token) {
    throw new Error('No token returned from tenant login')
  }

  authState.accessToken = token
  setAuthToken(token)

  const meResponse = await apiMe()
  const user = meResponse.data
  authState.user = user
  localStorage.setItem('user', JSON.stringify(user))

  if (['hr', 'executive', 'management'].includes(user.role)) {
    await router.push('/admin/companies')
  } else {
    await router.push('/chat')
  }

  return data
}

export function logout() {
  authState.accessToken = null
  authState.user = null
  setAuthToken(null)
  localStorage.removeItem('user')
  router.push('/login')
}
