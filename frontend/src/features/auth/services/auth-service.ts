/**
 * Authentication service.
 *
 * All backend authentication API calls are defined here.
 * Components and hooks call these functions — never Axios directly.
 *
 * Backend endpoints used:
 * - POST /auth/login  →  JWT token (form data: username=email, password)
 * - POST /auth/token  →  JWT token (form data: username=email, password)
 * - POST /users       →  Create user (JSON: full_name, email, password)
 */

import { apiClient } from '@/services/api-client';
import type {
  LoginRequest,
  RegisterRequest,
  ApiResponse,
  TokenResponse,
  UserResponse,
} from '../types';

/**
 * Authenticate a user with email and password.
 * Uses form data as required by the backend's OAuth2PasswordRequestForm dependency.
 */
export async function loginUser(
  data: LoginRequest,
): Promise<ApiResponse<TokenResponse>> {
  const formData = new URLSearchParams();
  formData.append('username', data.email);
  formData.append('password', data.password);

  const response = await apiClient.post<ApiResponse<TokenResponse>>(
    '/auth/login',
    formData.toString(),
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  );
  return response.data;
}

/**
 * Authenticate a user and return raw token response.
 * This endpoint returns TokenResponseSchema directly without the API envelope.
 */
export async function loginUserToken(
  data: LoginRequest,
): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', data.email);
  formData.append('password', data.password);

  const response = await apiClient.post<TokenResponse>(
    '/auth/token',
    formData.toString(),
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  );
  return response.data;
}

/**
 * Register a new user.
 * Backend endpoint: POST /api/v1/users
 */
export async function registerUser(
  data: RegisterRequest,
): Promise<ApiResponse<UserResponse>> {
  const response = await apiClient.post<ApiResponse<UserResponse>>(
    '/users',
    data,
  );
  return response.data;
}

/**
 * Fetch the currently authenticated user's profile.
 * Backend endpoint: GET /api/v1/users/{user_id}
 * Note: This requires the user's ID. For now, the auth context stores
 * the user data from registration. A dedicated /me endpoint can be added later.
 */
export async function fetchUser(
  userId: string,
): Promise<ApiResponse<UserResponse>> {
  const response = await apiClient.get<ApiResponse<UserResponse>>(
    `/users/${userId}`,
  );
  return response.data;
}
