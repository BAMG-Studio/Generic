const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Audit {
  id: string;
  repository: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  filesScanned: number;
  createdAt: string;
  completedAt?: string;
}

export interface UsageStats {
  filesScanned: number;
  apiRequests: number;
  storageUsed: number;
  monthlyLimit: number;
  tier: string;
  usageHistory: { date: string; count: number }[];
}

export interface ApiToken {
  id: string;
  name: string;
  token: string;
  createdAt: string;
  lastUsed: string | null;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const auditsApi = {
  async submit(repository: string): Promise<Audit> {
    const response = await fetch(`${API_BASE}/audits`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ repository }),
    });
    if (!response.ok) throw new Error('Failed to submit audit');
    return response.json();
  },

  async list(): Promise<{ audits: Audit[]; total: number }> {
    const response = await fetch(`${API_BASE}/audits`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch audits');
    return response.json();
  },

  async get(id: string): Promise<Audit> {
    const response = await fetch(`${API_BASE}/audits/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch audit');
    return response.json();
  },

  async downloadReport(id: string, format: 'json' | 'pdf' | 'html'): Promise<Blob> {
    const response = await fetch(`${API_BASE}/audits/${id}/report?format=${format}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download report');
    return response.blob();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/audits/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete audit');
  },
};

export const usageApi = {
  async getStats(): Promise<UsageStats> {
    const response = await fetch(`${API_BASE}/usage/stats`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch usage stats');
    return response.json();
  },
};

export const tokensApi = {
  async create(name: string): Promise<ApiToken> {
    const response = await fetch(`${API_BASE}/tokens`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name }),
    });
    if (!response.ok) throw new Error('Failed to create token');
    return response.json();
  },

  async list(): Promise<ApiToken[]> {
    const response = await fetch(`${API_BASE}/tokens`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch tokens');
    return response.json();
  },

  async revoke(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/tokens/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to revoke token');
  },
};
