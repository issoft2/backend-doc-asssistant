// authStore.ts
import { reactive } from 'vue'
import router from './router'
import axios from 'axios'
import {
  setAuthToken,
  removeAuthToken,
  login as apiLogin,
  me as apiMe,
  apiLogout,
  apiHeartbeat,
  type MeResponse,
} from './api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

type AuthState = {
  accessToken: string | null
  user: MeResponse | null
}

const savedToken = localStorage.getItem('access_token')
const savedUser = localStorage.getItem('user')

export const authState = reactive<AuthState>({
  accessToken: savedToken || null,
  user: savedUser ? (JSON.parse(savedUser) as MeResponse) : null,
})

function getUserPermissions(): string[] {
  return authState.user?.permissions || []
}

function hasAnyPermission(required: string[]): boolean {
  const current = getUserPermissions()
  return required.some(p => current.includes(p))
}

async function routeAfterLogin(): Promise<void> {
  // Treat anyone with admin-like config permissions as "admin view"
  const isAdminish = hasAnyPermission([
    'USER:CREATE',
    'ORG:ADMIN',
    'ORG:CREATE:SUB',
    'COLLECTION:CREATE',
    'DOC:UPLOAD',
  ])

  if (isAdminish) {
    await router.push('/admin/companies')
  } else {
    await router.push('/chat')
  }
}

export async function login(payload: { email: string; password: string }) {
  const { email, password } = payload
  const { data } = await apiLogin({ email, password })

  if (data.requires_tenant_selection) {
    // phase 1: vendor must choose tenant; no token yet
    return data
  }

  const token: string | undefined = data.access_token
  if (!token) {
    throw new Error('No token returned from login')
  }

  authState.accessToken = token
  setAuthToken(token)

  const { data: user } = await apiMe()
  authState.user = user
  localStorage.setItem('user', JSON.stringify(user))

  startHeartbeat()

  await routeAfterLogin()

  return data
}

export function startHeartbeat() {
  apiHeartbeat().catch(() => {
    // ignore heartbeat errors in FE
  })
}

export async function logout() {
  try {
    await apiLogout()
  } catch (e) {
    console.error('Error signing out of the system: ', e)
  }

  authState.accessToken = null
  authState.user = null
  localStorage.removeItem('user')
  localStorage.removeItem('access_token')
  removeAuthToken()

  await router.push('/')
}

export function firstLoginVerify(payload: { token: string }) {
  return api.post('/auth/first-login/verify', payload)
}

export function firstLoginSetPassword(payload: { token: string; new_password: string }) {
  return api.post('/auth/first-login/set-password', payload)
}

export async function loginToTenant(payload: { email: string; tenant_id: number }) {
  const { email, tenant_id } = payload

  const { data } = await api.post('/auth/login/tenant', {
    email,
    tenant_id,
  })

  const token: string | undefined = data.access_token
  if (!token) {
    throw new Error('No token returned from tenant login')
  }

  authState.accessToken = token
  setAuthToken(token)

  const { data: user } = await apiMe()
  authState.user = user
  localStorage.setItem('user', JSON.stringify(user))

  startHeartbeat()

  await routeAfterLogin()

  return data
}
