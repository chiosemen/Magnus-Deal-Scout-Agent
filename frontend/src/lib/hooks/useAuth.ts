import { useState, useEffect } from 'react';
import { authApi } from '@/lib/api';
import type { User, UserCreate, UserLogin } from '@/lib/types';
import { useRouter } from 'next/navigation';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: UserCreate) => {
    try {
      setLoading(true);
      setError(null);
      await authApi.register(data);
      // After registration, log the user in
      await login({ email: data.email, password: data.password });
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const login = async (data: UserLogin) => {
    try {
      setLoading(true);
      setError(null);
      await authApi.login(data);
      const profile = await authApi.getProfile();
      setUser(profile);
      router.push('/dashboard');
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      setUser(null);
      router.push('/auth/login');
    }
  };

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    checkAuth,
  };
}
