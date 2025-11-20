import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Document APIs
export const documentApi = {
  upload: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  getStructure: async (documentId) => {
    const response = await api.get(`/documents/${documentId}/structure`)
    return response.data
  },

  save: async (documentId, sectionsToUpdate, backup = true) => {
    const response = await api.post(`/documents/${documentId}/save`, {
      document_id: documentId,
      sections_to_update: sectionsToUpdate,
      backup,
    })
    return response.data
  },

  download: async (documentId) => {
    const response = await api.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  delete: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  },
}

// Content Generation APIs
export const contentApi = {
  generate: async (request) => {
    const response = await api.post('/content/generate', request)
    return response.data
  },

  compareModels: async (request) => {
    const response = await api.post('/content/compare-models', request)
    return response.data
  },

  getModels: async () => {
    const response = await api.get('/content/models')
    return response.data
  },

  getKnowledgeCollections: async () => {
    const response = await api.get('/content/knowledge-collections')
    return response.data
  },
}

// Review APIs
export const reviewApi = {
  conduct: async (request) => {
    const response = await api.post('/review/conduct', request)
    return response.data
  },

  analyzeTenses: async (request) => {
    const response = await api.post('/review/analyze-tenses', request)
    return response.data
  },

  applySuggestions: async (documentId, sectionId, suggestionIds) => {
    const response = await api.post(
      `/review/apply-suggestions/${documentId}/${sectionId}`,
      suggestionIds
    )
    return response.data
  },

  getReadability: async (documentId, sectionId) => {
    const response = await api.get(`/review/readability/${documentId}/${sectionId}`)
    return response.data
  },
}

// Config APIs
export const configApi = {
  getOpenWebUI: async () => {
    const response = await api.get('/config/openwebui')
    return response.data
  },

  updateOpenWebUI: async (config) => {
    const response = await api.post('/config/openwebui', config)
    return response.data
  },

  getPrompts: async () => {
    const response = await api.get('/config/prompts')
    return response.data
  },

  savePrompt: async (template) => {
    const response = await api.post('/config/prompts', template)
    return response.data
  },

  deletePrompt: async (templateId) => {
    const response = await api.delete(`/config/prompts/${templateId}`)
    return response.data
  },
}

// WebSocket for real-time content generation
export const createContentWebSocket = (clientId, onMessage) => {
  const wsUrl = API_BASE_URL.replace('http', 'ws')
  const ws = new WebSocket(`${wsUrl}/content/ws/generate/${clientId}`)

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }

  return ws
}

export default api
