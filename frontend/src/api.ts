// src/api.ts
import axios, { type AxiosError, type AxiosInstance } from 'axios'
import router from './router'

// ---- Axios instance ----
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

console.log('Axios baseURL:', api.defaults.baseURL)

// ---- Types ----
export interface MeResponse {
  id: string
  email: string
  role: string
  tenant_id?: string | null
  [key: string]: unknown
}

export interface ConfigureCompanyPayload {
  tenantId: string
  collectionName?: string
  plan: 'free_trial' | 'starter' | 'pro' | 'enterprise'
  subscription_status: 'trialing' | 'active' | 'expired' | 'cancelled'
}

export interface UploadDocumentPayload {
  tenantId: string
  collectionName: string
  title?: string
  file: File
  doc_id?: string
}

export interface SignupPayload {
  email: string
  password: string
  tenantId: string
  first_name?: string
  last_name?: string
  date_of_birth?: string
  phone?: string
  role?: string
  organization_id: string | number
}

export interface LoginPayload {
  email: string
  password: string
}

export interface QueryPoliciesPayload {
  question: string
  topK?: number
  conversationId?: string | null
}

export interface ListDriveFilesParams {
  folder_id?: string
}

export interface IngestDriveFilePayload {
  fileId: string
  collectionName: string
  title: string
}

export interface OrganizationOut {
  id: string
  tenant_id: string
  name: string
  type: 'umbrella' | 'subsidiary'
  parent_id: string | null
}

// ---- Basic helpers ----
export function me() {
  return api.get<MeResponse>('/auth/me')
}

// ---- Auth token helper ----
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
    localStorage.setItem('access_token', token)
  } else {
    delete api.defaults.headers.common.Authorization
    localStorage.removeItem('access_token')
  }
}

// On app startup, restore token
const saved = localStorage.getItem('access_token')
if (saved) {
  api.defaults.headers.common.Authorization = `Bearer ${saved}`
}

// ---- Global 401/403 interceptor ----
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      setAuthToken(null)
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  },
)

// Remove token (manual)
export function removeAuthToken() {
  delete api.defaults.headers.common.Authorization
}

// ---- Companies / collections ----
export function configureCompanyAndCollection(payload: ConfigureCompanyPayload) {
  const { tenantId, collectionName, plan, subscription_status } = payload
  return api.post('/companies/configure', {
    tenant_id: tenantId,
    collection_name: collectionName,
    plan,
    subscription_status,
  })
}

// List companies (admin listing page)
export function listCompanies() {
  return api.get('/companies')
}

// List collections for a company (admin listing page or tenant scoped)
export function listCollections(tenantId: string) {
  return api.get(`/companies/${tenantId}/collections`)
}

// Tenant-scoped collection creation (backend infers tenant from token)
export function createCollection({ name }: { name: string }) {
  return api.post('/collections', { name })
}

// ---- Company users ----
export function listCompanyUsers() {
  return api.get('/company/users')
}

export function getCompanyUser(userId: string) {
  return api.get(`/company/users/${userId}`)
}

export function updateCompanyUser(
  userId: string,
  payload: Record<string, unknown>,
) {
  return api.put(`/company/users/${userId}`, payload)
}

export function toggleCompanyUserActive(userId: string) {
  return api.post(`/company/users/${userId}/toggle-active`)
}

// ---- Documents ----
export function uploadDocument({
  tenantId,
  collectionName,
  title,
  file,
  doc_id,
}: UploadDocumentPayload) {
  const formData = new FormData()
  formData.append('tenant_id', tenantId)
  formData.append('collection_name', collectionName)
  if (title) formData.append('title', title)
  if (doc_id) formData.append('doc_id', doc_id)
  formData.append('file', file)

  return api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ---- Auth flows ----
export function signup({
  email,
  password,
  tenantId,
  first_name,
  last_name,
  date_of_birth,
  phone,
  role,
  organization_id,
}: SignupPayload) {
  return api.post('/auth/signup', {
    email,
    password,
    tenant_id: tenantId,
    first_name,
    last_name,
    date_of_birth,
    phone,
    role,
    organization_id,
  })
}

export function login({ email, password }: LoginPayload) {
  const data = new URLSearchParams()
  data.append('username', email)
  data.append('password', password)
  return api.post('/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function apiHeartbeat() {
  return api.post('/auth/users/heartbeat')
}

export function apiLogout() {
  return api.post('/auth/logout')
}

// ---- Chat / conversations ----
export function queryPolicies({
  question,
  topK = 5,
  conversationId,
}: QueryPoliciesPayload) {
  return api.post('/query', {
    question,
    top_k: topK,
    conversation_id: conversationId,
  })
}

export function listConversations() {
  return api.get('/conversations')
}

export function getConversation(conversationId: string) {
  return api.get(`/conversations/${conversationId}`)
}

export function deleteConversation(conversationId: string) {
  return api.delete(`/conversations/${conversationId}`)
}

// ---- Google Drive connections for ingest ----
export function getGoogleDriveAuthUrl() {
  return api.get('/google-drive/auth-url')
}

export function getGoogleDriveStatus() {
  return api.get('/google-drive/status')
}

export function listDriveFiles(params?: ListDriveFilesParams) {
  return api.get('/google-drive/files', {
    params: params || {},
  })
}

export function ingestDriveFile(payload: IngestDriveFilePayload) {
  return api.post('/google-drive/ingest', {
    file_id: payload.fileId,
    collection_name: payload.collectionName,
    title: payload.title,
  })
}

export function disconnectGoogleDriveApi() {
  return api.post('/google-drive/disconnect')
}

// ---- Misc ----
export function sendContact(payload: Record<string, unknown>) {
  return api.post('/contact', payload)
}

// ---- Organizations (new backend) ----
export async function fetchOrganizations() {
  const { data } = await api.get<OrganizationOut[]>('/organizations')
  return data
}


export function createOrganizationForTenant(
  tenantId: string,
  payload: {
    name: string
    type: 'umbrella' | 'subsidiary'
  },
) {
  return api.post<OrganizationOut>('/organizations', {
    tenant_id: tenantId,
    ...payload,
  })
}



export interface CreateOrganizationPayload {
  name: string
  type: 'umbrella' | 'subsidiary'
  parent_id?: string | null
}

export function createOrganization(payload: CreateOrganizationPayload) {
  return api.post<OrganizationOut>('/organizations', payload)
}

export function createCollectionForOrganization(
  tenantId: string,
  organizationId: string | number,
  payload: {
    name: string
  },
) {
  return api.post(
    `/tenants/${tenantId}/organizations/${organizationId}/collections`,
    payload,
  )
}

