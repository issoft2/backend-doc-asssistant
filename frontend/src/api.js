import axios from 'axios'
import router from './router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api", 
})
console.log("Axios baseURL:", api.defaults.baseURL)
export function me() {
  return api.get('/auth/me')
}

// ---- auth token helper ----
export function setAuthToken(token) {
    if (token) {
        api.defaults.headers.common.Authorization = `Bearer ${token}`
        localStorage.setItem('access_token', token)
    } else {
        delete api.defaults.headers.common.Authorization
        localStorage.removeItem('access_token')
    }
}

// On app startup, restore token:
const saved = localStorage.getItem('access_token')
if (saved) {
    api.defaults.headers.common.Authorization = `Bearer ${saved}`
}

// ----- global 401 header --------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // clear auth and redirect to login
      setAuthToken(null)
      // avoid redirect loop if already on login
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

// Configure company + collection in one step
export function configureCompanyAndCollection({ tenantId, collectionName }) {
  return api.post('/companies/configure', {
    tenant_id: tenantId,
    collection_name: collectionName,
  })
}

// List companies (admin listing page)
export function listCompanies() {
  return api.get('/companies')
}

// List collections for a company (admin listing page)
export function listCollections(tenantId) {
  return api.get(`/companies/${tenantId}/collections`)
}


// List all users (admin only)
export function listCompanyUsers() {
  console.log("I am looking...............")
  return api.get('/company/users')
}

// Get single user (if need for detail/edit view)
export function getCompanyUser(userId) {
  return api.get(`/company/users/${userId}`)
}

// Update user
export function updateCompanyUser(userId, payload) {
  // payload matches userUpdate shape: {first_name?, last_name?, date_of_birth?, phone?, role?, is_active?}
  return api.put(`/company/users/${userId}`, payload)
}

// Toggle active / inactive
export function toggleCompanyUserActive(userId) {
  return api.post(`/company/users/${userId}/toggle-active`)
}

// Upload document to current tenant + collection
export function uploadDocument({ tenantId, collectionName, title, file, doc_id }) {
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

export function signup({email, password, tenantId, first_name, last_name, date_of_birth, phone, role}) {
    return api.post('/auth/signup', {
        email,
        password,
        tenant_id: tenantId,
        first_name,
        last_name,
        date_of_birth,
        phone,
        role

    })
}

export function login({ email, password }) {
    const data = new URLSearchParams()
    data.append('username', email)
    data.append('password', password)
    return api.post('/auth/login', data, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
    })
}


// Employee chat query
export function queryPolicies({ question, topK = 5, conversationId}) {
  return api.post('/query', {
    question,
    top_k: topK,
    conversation_id: conversationId,
  })
}

export function listConversations() {
  return api.get('/conversations')
}

export function getConversation(conversationId) {
  return api.get(`/conversations/${conversationId}`)
}

// api.js
export function createCollection({ name }) {
  return api.post('/collections', {
    name,
  })
}

export function deleteConversation(conversationId) {
  return api.delete(`/conversations/${conversationId}`)
}

