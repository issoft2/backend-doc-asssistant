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
  id: number
  email: string
  role: string
  tenant_id: number
  organization_id: number | null
  roles: string[]
  permissions: string[]
  first_name?: string | null
  last_name?: string | null
  date_of_birth?: string | null
  phone?: string | null
  is_active?: boolean
  created_at?: string
  is_online?: boolean
  last_login_at?: string | null
  last_seen_at?: string | null
  [key: string]: unknown
}


export interface ConfigureCompanyPayload {
  tenant_id: string
  plan: 'free_trial' | 'starter' | 'pro' | 'enterprise'
  subscription_status: 'trialing' | 'active' | 'expired' | 'cancelled'
}

export interface UploadDocumentPayload {
  collectionName: string
  title?: string
  file: File
  doc_id?: string
}

export interface SignupPayload {
  email: string
  password: string
  tenant_id?: number          // optional if BE infers from token
  first_name?: string
  last_name?: string
  date_of_birth?: string
  phone?: string
  role?: string
  organization_id: number
  
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
}

export interface  CollectionOut{
  id: string
  tenant_id: string
  name: string
  organization_id: string
  doc_count: number
  visibility: 'tenant' | 'org' | 'role' | 'user' // match your enum
  allowed_roles: string[]
  allowed_user_ids: string[]
  rceated_at: string
  updated_at: string

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
export function configureTenantPayload(payload: ConfigureCompanyPayload) {
  const { tenant_id, plan, subscription_status } = payload
  return api.post('/companies/configure', {
    tenant_id: tenant_id,
    plan,
    subscription_status,
  })
}

// List companies (admin listing page)
export function listCompanies() {
  return api.get('/companies')
}

// List Organization---
export async function fetchOrganizations(
  tenant_id: string,
): Promise<OrganizationOut[]> {
  const { data } = await api.get<OrganizationOut[]>('/organizations', {
    params: { tenant_id },
  })

  return data
}


// List collections for a company (admin listing page or tenant scoped)
export  async function listCollectionsForTenant(
  tenant_id: String,
): Promise<CollectionOut[]>{
  const { data } = await api.get<CollectionOut[]>('collections', {
   params: {tenant_id },
  })
  return data

}


export async function ListCollectionForOrg() {
  return api.get('/collection/by_org')
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

export function listOrgTenantUsers() {
  return api.get('/organizations/users')
}

// ---- Documents ----
export function uploadDocument({
  collectionName,
  title,
  file,
  doc_id,
}: UploadDocumentPayload) {
  const formData = new FormData()
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
  tenant_id,
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
    ...(tenant_id != null ? { tenant_id } : {}),
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


export function createOrganizationForTenant(
  tenant_id: string,
  payload: {
    name: string
  },
) {
  return api.post<OrganizationOut>('/organizations', {
    tenant_id: tenant_id,
    ...payload,
  })
}



export interface CreateOrganizationPayload {
  name: string
}

export function createOrganization(payload: CreateOrganizationPayload) {
  return api.post<OrganizationOut>('/organizations', payload)
}

// align with CollectionCreateIn
export function createCollectionForOrganization(payload: {
  tenant_id: string
  organization_id: number | null
  name: string
  visibility: 'tenant' | 'org' | 'role' | 'user'
  allowed_roles: string[]
  allowed_user_ids: string[]
}) {
  return api.post('/collections/create', payload)
}

/** Get collection ACL (allowed_user_ids + allowed_roles) */
export async function getCollectionAccess(collectionId: string | number) {
  const res = await api.get(`/collections/${collectionId}/access`)
  return res
}

/** Update collection ACL */
export async function updateCollectionAccess(
  collectionId: string | number,
  payload: {
    allowed_user_ids: string[]
    allowed_roles: string[]
  },
) {
  const res = await api.put(
    `/collections/${collectionId}/access`,
    payload,
  )
  return res
}


