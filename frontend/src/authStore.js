// authStore.js
import { reactive } from 'vue'
import router from './router'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api", 
})

import { setAuthToken, removeAuthToken, login as apiLogin, me as apiMe, apiLogout, apiHeartbeat } from './api'

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

  // 🔹 start heartbeat once user is in
  startHeartbeat()

  if (['hr', 'executive', 'management', 'admin'].includes(user.role)) {
    await router.push('/admin/companies')
  } else {
    await router.push('/chat')
  }

  return data
}

let heartbeatId

export async function startHeartbeat() {
  if (heartbeatId) return
  heartbeatId = window.setInterval(() => {
    apiHeartbeat().catch(() => {})
  }, 30_000)
}

export async function logout() {
  try {
    await apiLogout()
  } catch (e) {}
  
  if (heartbeatId) {
    clearInterval(heartbeatId)
    heartbeatId = undefined
  }
  authState.accessToken = null
  authState.user = null
  localStorage.removeItem('user')
  removeAuthToken
  await router.push('/')
}


export function firstLoginVerify(payload) {
  return api.post('/auth/first-login/verify', payload)
}

export function firstLoginSetPassword(payload) {
  return api.post('/auth/first-login/set-password', payload)
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

  if (['hr', 'executive', 'management', 'admin'].includes(user.role)) {
    await router.push('/admin/companies')
  } else {
    await router.push('/chat')
  }

  return data
}

