import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (data: { email: string; password: string; full_name: string; company_name: string }) =>
    api.post('/auth/signup', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  getMe: () => api.get('/auth/me'),
};

// Repository API
export const repositoryAPI = {
  list: () => api.get('/repositories'),
  
  create: (data: {
    name: string;
    full_name: string;
    provider: string;
    clone_url: string;
    default_branch?: string;
    description?: string;
    is_private?: boolean;
  }) => api.post('/repositories', data),
  
  get: (id: string) => api.get(`/repositories/${id}`),
};

// Scan API
export const scanAPI = {
  list: (params?: { repository_id?: string; limit?: number; offset?: number }) =>
    api.get('/scans', { params }),
  
  create: (data: {
    repository_id: string;
    branch?: string;
    commit_sha?: string;
    scan_type?: string;
  }) => api.post('/scans', data),
  
  get: (id: string) => api.get(`/scans/${id}`),
};

// Consent API
export const consentAPI = {
  list: () => api.get('/consent'),
  
  create: (data: {
    consent_type: string;
    consent_state: boolean;
    scan_id?: string;
  }) => api.post('/consent', data),
  
  revoke: (id: string) => api.patch(`/consent/${id}/revoke`),
};
