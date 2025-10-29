import apiClient from './client';
import type { User, UserCreate, UserLogin, Token } from '@/lib/types';

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.axios.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login user
   */
  login: async (data: UserLogin): Promise<Token> => {
    const formData = new URLSearchParams();
    formData.append('username', data.email);
    formData.append('password', data.password);

    const response = await apiClient.axios.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store tokens
    apiClient.setTokens(response.data.access_token, response.data.refresh_token);

    return response.data;
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.axios.post('/auth/logout');
    } finally {
      // Clear tokens even if API call fails
      apiClient.clearTokens();
    }
  },

  /**
   * Get current user profile
   */
  getProfile: async (): Promise<User> => {
    const response = await apiClient.axios.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Refresh access token
   */
  refresh: async (refreshToken: string): Promise<Token> => {
    const response = await apiClient.axios.post<Token>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    // Update access token
    apiClient.setAccessToken(response.data.access_token);

    return response.data;
  },
};
