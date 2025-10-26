// src/lib/api/auth.ts

import apiClient from './client';
import { AuthTokens, User, LoginCredentials, RegisterData } from '../types';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await apiClient.post<AuthTokens>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    apiClient.setToken(response.access_token);
    return response;
  },

  async register(data: RegisterData): Promise<User> {
    return apiClient.post<User>('/auth/register', data);
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  },

  async logout(): Promise<void> {
    apiClient.clearToken();
  },

  async refreshToken(): Promise<AuthTokens> {
    const response = await apiClient.post<AuthTokens>('/auth/refresh');
    apiClient.setToken(response.access_token);
    return response;
  },

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return apiClient.post('/auth/password-reset/request', { email });
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post('/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
    });
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    return apiClient.post('/auth/verify-email', { token });
  },
};
