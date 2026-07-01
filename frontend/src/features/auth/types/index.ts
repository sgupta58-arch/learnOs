/**
 * Authentication types matching backend API schemas.
 *
 * These types mirror the backend's auth and user schemas.
 * Never deviate from the backend contract — these are the source of truth.
 */

/** Login request payload sent to POST /api/v1/auth/login */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Registration request payload sent to POST /api/v1/users */
export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

/** JWT token response from POST /api/v1/auth/login or /auth/token */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/** Standard API error detail matching backend ErrorDetail schema */
export interface ApiErrorDetail {
  field?: string | null;
  message: string;
}

/** Standard API response envelope matching backend ApiResponse schema */
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  errors: ApiErrorDetail[];
  data: T | null;
}

/** User response schema matching backend UserResponseSchema */
export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  profile_picture: string | null;
  created_at: string;
  updated_at: string;
}

/** Authentication state for the AuthContext */
export interface AuthState {
  isAuthenticated: boolean;
  isInitialized: boolean;
  user: UserResponse | null;
}