import axios from 'axios';
import {
  Job,
  JobListResponse,
  JobStats,
  FilterOptions,
  TokenResponse,
  User,
  SavedJob,
  SavedJobListResponse,
  JobAlert,
  JobAlertListResponse,
  AlertMatchResponse,
  UserProfileMatch,
  MatchedJobListResponse,
  SingleJobMatchResponse,
  IngestionRunResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token if invalid or expired
      const hasToken = localStorage.getItem('access_token');
      if (hasToken && !error.config.url?.includes('/auth/login')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-unauthorized'));
      }
    }
    return Promise.reject(error);
  }
);

// =============================================
// JOBS API
// =============================================
export const jobsApi = {
  getJobs: async (params?: {
    limit?: number;
    offset?: number;
    search?: string;
    company?: string[];
    employment_type?: string[];
    location?: string[];
    seniority?: string[];
    category?: string[];
    minimum_salary?: number;
    sort_by?: string;
    sort_order?: string;
    include_expired?: boolean;
    include_deleted?: boolean;
  }): Promise<JobListResponse> => {
    const res = await apiClient.get<JobListResponse>('/jobs', { params });
    return res.data;
  },

  getJobById: async (jobId: number): Promise<Job> => {
    const res = await apiClient.get<Job>(`/jobs/${jobId}`);
    return res.data;
  },

  getSimilarJobs: async (
    jobId: number,
    limit = 10,
    minScore = 0.1
  ): Promise<JobListResponse> => {
    const res = await apiClient.get<JobListResponse>(`/jobs/${jobId}/similar`, {
      params: { limit, min_score: minScore },
    });
    return res.data;
  },

  ftsSearchJobs: async (
    q: string,
    params?: {
      limit?: number;
      offset?: number;
      company?: string[];
      location?: string[];
      category?: string[];
    }
  ): Promise<JobListResponse> => {
    const res = await apiClient.get<JobListResponse>('/jobs/fts/search', {
      params: { q, ...params },
    });
    return res.data;
  },

  getJobStats: async (): Promise<JobStats> => {
    const res = await apiClient.get<JobStats>('/jobs/stats');
    return res.data;
  },

  getFilterOptions: async (): Promise<FilterOptions> => {
    const res = await apiClient.get<FilterOptions>('/jobs/filters');
    return res.data;
  },

  softDeleteJob: async (jobId: number): Promise<Job> => {
    const res = await apiClient.delete<Job>(`/jobs/${jobId}`);
    return res.data;
  },

  restoreJob: async (jobId: number): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${jobId}/restore`);
    return res.data;
  },
};

// =============================================
// AUTH API
// =============================================
export const authApi = {
  register: async (payload: {
    email: string;
    password: string;
    full_name?: string;
  }): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/register', payload);
    return res.data;
  },

  login: async (payload: {
    email: string;
    password: string;
  }): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/login', payload);
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return res.data;
  },
};

// =============================================
// SAVED JOBS API
// =============================================
export const savedJobsApi = {
  getSavedJobs: async (limit = 20, offset = 0): Promise<SavedJobListResponse> => {
    const res = await apiClient.get<SavedJobListResponse>('/saved-jobs', {
      params: { limit, offset },
    });
    return res.data;
  },

  saveJob: async (jobId: number, notes?: string): Promise<SavedJob> => {
    const res = await apiClient.post<SavedJob>(`/saved-jobs/${jobId}`, {
      notes,
    });
    return res.data;
  },

  unsaveJob: async (jobId: number): Promise<{ message: string; job_id: number }> => {
    const res = await apiClient.delete<{ message: string; job_id: number }>(
      `/saved-jobs/${jobId}`
    );
    return res.data;
  },

  checkSavedStatus: async (
    jobId: number
  ): Promise<{ job_id: number; is_saved: boolean }> => {
    const res = await apiClient.get<{ job_id: number; is_saved: boolean }>(
      `/saved-jobs/${jobId}/check`
    );
    return res.data;
  },
};

// =============================================
// JOB ALERTS API
// =============================================
export const alertsApi = {
  getAlerts: async (limit = 20, offset = 0): Promise<JobAlertListResponse> => {
    const res = await apiClient.get<JobAlertListResponse>('/alerts', {
      params: { limit, offset },
    });
    return res.data;
  },

  createAlert: async (payload: {
    name: string;
    keywords?: string;
    location?: string;
    category?: string;
    seniority?: string;
    min_salary?: number;
    frequency?: string;
    is_active?: boolean;
  }): Promise<JobAlert> => {
    const res = await apiClient.post<JobAlert>('/alerts', payload);
    return res.data;
  },

  updateAlert: async (
    alertId: number,
    payload: Partial<JobAlert>
  ): Promise<JobAlert> => {
    const res = await apiClient.put<JobAlert>(`/alerts/${alertId}`, payload);
    return res.data;
  },

  deleteAlert: async (alertId: number): Promise<{ message: string; alert_id: number }> => {
    const res = await apiClient.delete<{ message: string; alert_id: number }>(
      `/alerts/${alertId}`
    );
    return res.data;
  },

  testMatch: async (alertId: number): Promise<AlertMatchResponse> => {
    const res = await apiClient.post<AlertMatchResponse>(
      `/alerts/${alertId}/test-match`
    );
    return res.data;
  },
};

// =============================================
// JOB MATCHING API
// =============================================
export const matchingApi = {
  matchJobs: async (
    profile: UserProfileMatch,
    limit = 10,
    minScore = 0.1
  ): Promise<MatchedJobListResponse> => {
    const res = await apiClient.post<MatchedJobListResponse>('/match', profile, {
      params: { limit, min_score: minScore },
    });
    return res.data;
  },

  matchSingleJob: async (
    jobId: number,
    profile: UserProfileMatch
  ): Promise<SingleJobMatchResponse> => {
    const res = await apiClient.post<SingleJobMatchResponse>(
      `/match/${jobId}`,
      profile
    );
    return res.data;
  },
};

// =============================================
// ADMIN INGESTION API
// =============================================
export const adminApi = {
  runIngestion: async (maxPages = 5, pageSize = 20): Promise<IngestionRunResponse> => {
    const res = await apiClient.post<IngestionRunResponse>('/ingestion/run', {
      max_pages: maxPages,
      page_size: pageSize,
    });
    return res.data;
  },
};
