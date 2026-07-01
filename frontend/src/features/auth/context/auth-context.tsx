import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { loginUser, registerUser } from '../services/auth-service';
import { tokenStorage } from '../utils/token-storage';
import type { AuthState, LoginRequest, RegisterRequest } from '../types';

interface AuthContextValue extends AuthState {
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Authentication provider.
 *
 * Manages authentication state across the application.
 * Responsibilities:
 * - Session restoration on app startup
 * - Login and registration via TanStack Query mutations
 * - Logout with state and cache cleanup
 * - Exposing auth state to all child components
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isInitialized: false,
    user: null,
  });

  // --- Session restoration on mount ---
  useEffect(() => {
    const token = tokenStorage.get();
    if (token) {
      setState({
        isAuthenticated: true,
        isInitialized: true,
        user: null,
      });
    } else {
      setState({
        isAuthenticated: false,
        isInitialized: true,
        user: null,
      });
    }
  }, []);

  // --- Login mutation ---
  const loginMutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (response) => {
      if (response.success && response.data) {
        tokenStorage.set(response.data.access_token);
        setState({
          isAuthenticated: true,
          isInitialized: true,
          user: null,
        });
      } else {
        throw new Error(response.message || 'Login failed');
      }
    },
  });

  // --- Register mutation ---
  const registerMutation = useMutation({
    mutationFn: registerUser,
    onSuccess: (response) => {
      if (response.success && response.data) {
        setState({
          isAuthenticated: false,
          isInitialized: true,
          user: response.data,
        });
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    },
  });

  // --- Login action ---
  const login = useCallback(
    async (data: LoginRequest) => {
      await loginMutation.mutateAsync(data);
    },
    [loginMutation],
  );

  // --- Register action ---
  const register = useCallback(
    async (data: RegisterRequest) => {
      await registerMutation.mutateAsync(data);
    },
    [registerMutation],
  );

  // --- Logout action ---
  const logout = useCallback(() => {
    tokenStorage.remove();
    queryClient.clear();
    setState({
      isAuthenticated: false,
      isInitialized: true,
      user: null,
    });
  }, [queryClient]);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      register,
      logout,
    }),
    [state, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context.
 * Must be used within an AuthProvider.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}