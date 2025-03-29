import axios from 'axios';

// Types for our API responses
export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  type: string;
  created_at: string;
  updated_at: string;
}

export interface Container {
  id: number;
  name: string;
  type: string;
  project_id: number;
  items_count?: number;
  created_at: string;
  updated_at: string;
}

export interface DataItem {
  id: number;
  content: string;
  metadata?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface ImportProgress {
  import_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  processed_rows: number;
  total_rows: number;
  container_id?: number;
  error?: string;
  metadata_columns?: Record<string, string>;
}

export interface ImportResponse {
  message: string;
  import_id: string;
}

export interface ValidateCSVResponse {
  valid: boolean;
  total_rows: number;
  columns: string[];
  column_mapping: Record<string, string>;
}

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions for authentication
export const auth = {
  login: async (username: string, password: string) => {
    // FastAPI expects form data for OAuth2 password flow
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password');

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  },
};

// API functions for users
export const users = {
  list: async (): Promise<User[]> => {
    const response = await api.get('/admin-api/users');
    return response.data;
  },
  create: async (userData: Omit<User, 'id'>) => {
    const response = await api.post('/admin-api/users', userData);
    return response.data;
  },
  delete: async (id: number) => {
    await api.delete(`/admin-api/users/${id}`);
  },
};

// API functions for projects
export const projects = {
  list: async (): Promise<Project[]> => {
    const response = await api.get('/admin-api/projects');
    return response.data;
  },

  get: async (id: number): Promise<Project> => {
    const response = await api.get(`/admin-api/projects/${id}`);
    return response.data;
  },

  create: async (projectData: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post('/admin-api/projects', projectData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/admin-api/projects/${id}`);
  },

  addUser: async (projectId: number, userId: number) => {
    await api.post(`/admin-api/projects/${projectId}/users/${userId}`);
  },

  removeUser: async (projectId: number, userId: number) => {
    await api.delete(`/admin-api/projects/${projectId}/users/${userId}`);
  },

  listContainers: async (projectId: number): Promise<Container[]> => {
    const response = await api.get(`/admin-api/projects/${projectId}/containers`);
    return response.data;
  },
};

// API functions for containers
export const containers = {
  list: async (): Promise<Container[]> => {
    const response = await api.get('/admin-api/containers');
    return response.data;
  },

  get: async (id: number): Promise<Container> => {
    const response = await api.get(`/admin-api/containers/${id}`);
    return response.data;
  },

  create: async (containerData: Omit<Container, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post('/admin-api/containers', containerData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/admin-api/containers/${id}`);
  },

  listItems: async (id: number): Promise<DataItem[]> => {
    const response = await api.get(`/admin-api/containers/${id}/items`);
    return response.data;
  },
};

// API functions for imports
export const imports = {
  validateCSV: async (file: File, metadata_columns?: string): Promise<ValidateCSVResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata_columns) {
      formData.append('metadata_columns', metadata_columns);
    }

    const response = await api.post('/chat-disentanglement/validate-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  importChatRoom: async (
    projectId: number,
    file: File,
    name: string,
    metadata_columns?: string,
    container_id?: number,
    batch_size: number = 1000
  ): Promise<ImportResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    if (metadata_columns) {
      formData.append('metadata_columns', metadata_columns);
    }
    if (container_id) {
      formData.append('container_id', container_id.toString());
    }
    formData.append('batch_size', batch_size.toString());

    const response = await api.post(
      `/chat-disentanglement/projects/${projectId}/rooms/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  getProgress: async (importId: string): Promise<ImportProgress> => {
    const response = await api.get(`/chat-disentanglement/imports/${importId}`);
    return response.data;
  },

  cancel: async (importId: string): Promise<{ message: string }> => {
    const response = await api.post(`/chat-disentanglement/imports/${importId}/cancel`);
    return response.data;
  },

  retry: async (importId: string): Promise<{ message: string; import_id: string }> => {
    const response = await api.post(`/chat-disentanglement/imports/${importId}/retry`);
    return response.data;
  },
};

export default api;