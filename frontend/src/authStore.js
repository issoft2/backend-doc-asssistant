// authStore.js
import { reactive } from 'vue'
import router from './router'
import { setAuthToken, login as apiLogin, me as apiMe } from './api'

export const authState = reactive({
  accessToken: localStorage.getItem('access_token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
})

export async function login({ email, password }) {
  // 1) login to get token
  const { data: tokenData } = await apiLogin({ email, password })
  const token = tokenData.access_token
  authState.accessToken = token
  setAuthToken(token)

  // 2) fetch current user (includes role, tenant_id, etc.)
  const { data: user } = await apiMe()
  authState.user = user
  localStorage.setItem('user', JSON.stringify(user))

  // 3) redirect based on role
  if (['hr', 'executive', 'management'].includes(user.role)) {
    await router.push('/admin/companies') // or /admin/ingest – your choice
  } else {
    await router.push('/chat')
  }
}

export async function loginToTenant({ email, tenant_id }) {
  const res = await api.post('/login/tenant', { email, tenant_id })

  const token = res.data.access_token
  if (!token) {
    throw new Error("No token returned from tenant login")
  }

  // store token (adapt to your existing pattern)
  authState.token = token
  localStorage.setItem('access_token', token)

  // optionally decode token to set authState.user /tenantId
  // const payload = JSON.parse(atob(token.split('.)[1]))

  // redirect to main app, e.g. chat or admin
  router.push('/chat')
}

export function logout() {
  authState.accessToken = null
  authState.user = null
  setAuthToken(null)
  localStorage.removeItem('user')
  router.push('/login')
}
