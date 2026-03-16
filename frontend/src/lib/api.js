import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  signin: (data) => api.post('/auth/signin', data),
  getProfile: (userId) => api.get(`/auth/profile/${userId}`)
}

export const jobsAPI = {
  submit: (data) => api.post('/jobs/submit', data),
  getStatus: (id) => api.get(`/jobs/status/${id}`),
  getResult: (id) => api.get(`/jobs/result/${id}`),
  getStats: () => api.get('/jobs/queue/stats')
}

export const proteinsAPI = {
  getInfo: (pdbId) => api.get(`/proteins/info/${pdbId}`),
  search: (disease) => api.get(`/proteins/search/${disease}`)
}

export const agentAPI = {
  getLogs: (experimentId) => api.get(`/agent/logs/${experimentId}`)
}

export const experimentsAPI = {
  list: (userId) => api.get(`/experiments/list/${userId}`),
  get: (id) => api.get(`/experiments/${id}`)
}

export default api
