// src/lib/hooks/useAuth.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api';
import { LoginCredentials, RegisterData, User } from '../types';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Welcome back!');
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterData) => authApi.register(data),
    onSuccess: () => {
      toast.success('Account created successfully! Please log in.');
      router.push('/login');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.');
    },
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authApi.getCurrentUser(),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      queryClient.clear();
      toast.success('Logged out successfully');
      router.push('/login');
    },
  });
}
