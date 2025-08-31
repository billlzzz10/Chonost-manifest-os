/**
 * API Client for Chat Integration Backend
 * 
 * This module provides a centralized API client for communicating
 * with the backend services.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['x-access-token'] = this.token;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // HTTP Methods
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    const headers = {};
    if (this.token) {
      headers['x-access-token'] = this.token;
    }

    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: formData,
    });
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Export specific API methods for different features
export const authApi = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: () => apiClient.post('/auth/refresh'),
};

export const chatApi = {
  getSessions: () => apiClient.get('/chat/sessions'),
  createSession: (data) => apiClient.post('/chat/sessions', data),
  getMessages: (sessionId) => apiClient.get(`/chat/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, message) => apiClient.post(`/chat/sessions/${sessionId}/messages`, message),
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),
};

export const fileApi = {
  uploadFile: (file, type = 'general') => apiClient.uploadFile('/files/upload', file, { type }),
  getFiles: (params = {}) => apiClient.get('/files/list', params),
  getFileInfo: (fileId) => apiClient.get(`/files/${fileId}/info`),
  downloadFile: (fileId) => apiClient.get(`/files/${fileId}`),
  deleteFile: (fileId) => apiClient.delete(`/files/${fileId}`),
};

export const automationApi = {
  getWorkflows: () => apiClient.get('/automation/workflows'),
  createWorkflow: (data) => apiClient.post('/automation/workflows', data),
  updateWorkflow: (id, data) => apiClient.put(`/automation/workflows/${id}`, data),
  deleteWorkflow: (id) => apiClient.delete(`/automation/workflows/${id}`),
  executeWorkflow: (id, inputData) => apiClient.post(`/automation/workflows/${id}/execute`, { input_data: inputData }),
  getExecutions: (workflowId) => apiClient.get(`/automation/workflows/${workflowId}/executions`),
};

export const connectionApi = {
  getConnections: () => apiClient.get('/automation/connections'),
  createConnection: (data) => apiClient.post('/automation/connections', data),
  updateConnection: (id, data) => apiClient.put(`/automation/connections/${id}`, data),
  deleteConnection: (id) => apiClient.delete(`/automation/connections/${id}`),
  testConnection: (id) => apiClient.post(`/automation/connections/${id}/test`),
};

export const templateApi = {
  getTemplates: (params = {}) => apiClient.get('/automation/templates', params),
  createTemplate: (data) => apiClient.post('/automation/templates', data),
  updateTemplate: (id, data) => apiClient.put(`/automation/templates/${id}`, data),
  deleteTemplate: (id) => apiClient.delete(`/automation/templates/${id}`),
  useTemplate: (id, data) => apiClient.post(`/automation/templates/${id}/use`, data),
};

