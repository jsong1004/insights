/**
 * API Wrapper Module
 * Provides typed fetch utilities for backend communication
 */

import type { APIResponse } from './types';

/**
 * API configuration
 */
const API_CONFIG = {
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Custom API Error class
 */
export class APIException extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIException';
  }
}

/**
 * Make a typed API request
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_CONFIG.baseURL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      ...API_CONFIG.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    // Parse JSON response
    let data: APIResponse<T>;
    try {
      data = await response.json();
    } catch {
      // If JSON parsing fails, create error response
      throw new APIException(
        'Invalid JSON response from server',
        'INVALID_JSON'
      );
    }

    // Handle non-2xx responses
    if (!response.ok) {
      throw new APIException(
        data.error || data.message || 'API request failed',
        'HTTP_ERROR',
        { status: response.status, data }
      );
    }

    // Check for application-level errors
    if (!data.success) {
      throw new APIException(
        data.error || data.message || 'Request failed',
        'APP_ERROR',
        data
      );
    }

    return data.data as T;
  } catch (error) {
    if (error instanceof APIException) {
      throw error;
    }

    // Network or other errors
    throw new APIException(
      error instanceof Error ? error.message : 'Network error',
      'NETWORK_ERROR'
    );
  }
}

/**
 * API object with typed methods
 */
export const API = {
  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = params
      ? `${endpoint}?${new URLSearchParams(params).toString()}`
      : endpoint;
    return request<T>(url, { method: 'GET' });
  },

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: 'DELETE' });
  },

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },
};

/**
 * Specific API endpoints with typed responses
 */
export const InsightsAPI = {
  /**
   * Pin or unpin an insight (admin only)
   */
  async pinInsight(insightId: string, isPinned: boolean): Promise<{ success: boolean; is_pinned: boolean; message: string }> {
    return API.post(`/api/insights/${insightId}/pin`, { is_pinned: isPinned });
  },

  /**
   * Get community statistics
   */
  async getCommunityStats(): Promise<{ total_insights: number; total_likes: number; total_authors: number; trending_topics: any[] }> {
    return API.get('/api/community-stats');
  },

  /**
   * Get trending topics
   */
  async getTrendingTopics(limit: number = 10): Promise<{ topic: string; count: number }[]> {
    const response = await API.get<{ topics: any[] }>('/api/trending-topics', { limit });
    return response.topics;
  },

  /**
   * Like an insight
   */
  async likeInsight(insightId: string): Promise<{ success: boolean; liked: boolean; likes: number }> {
    return API.post(`/api/insights/${insightId}/like`);
  },

  /**
   * Toggle sharing status
   */
  async toggleSharing(insightId: string, isShared: boolean): Promise<{ success: boolean; is_shared: boolean }> {
    return API.post(`/api/insights/${insightId}/share`, { is_shared: isShared });
  },
};

/**
 * Initialize API (called from main.ts)
 */
export function initializeAPI(): void {
  console.log('[API] API module initialized');
}

/**
 * Export for global access
 */
if (typeof window !== 'undefined') {
  (window as any).API = API;
  (window as any).InsightsAPI = InsightsAPI;
}
