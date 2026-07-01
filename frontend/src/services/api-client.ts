/**
 * Axios HTTP client infrastructure.
 *
 * Centralized Axios instance with interceptors for:
 * - Base URL from environment configuration
 * - Request interceptor: attaches JWT to every request
 * - Response interceptor: handles 401 unauthorized (logout)
 */

import axios from 'axios';
import { env } from '@/config/env';
import { tokenStorage } from '@/features/auth/utils/token-storage';

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: 15_000,
 
});

/**
 * Request interceptor.
 * Attaches the JWT access token to every outgoing request
 * if a token exists in storage.
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenStorage.get();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

/**
 * Response interceptor.
 * Handles 401 Unauthorized responses by clearing the stored token.
 * This ensures that expired/invalid tokens don't leave the app in a
 * broken auth state. The AuthContext's session restoration will detect
 * the missing token on next app load.
 *
 * Note: Token refresh is not implemented — the backend may support it
 * in the future. When it does, this interceptor is the place to add it.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      tokenStorage.remove();
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);