/**
 * Shared TypeScript types for the application.
 *
 * This module exports common types used across features.
 * Feature-specific types should live in their respective feature folders.
 */

/** Generic pagination parameters for list endpoints. */
export interface PaginationParams {
  page?: number;
  pageSize?: number;
}

/** Generic paginated response wrapper. */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/** Standard API error response. */
export interface ApiError {
  statusCode: number;
  message: string;
  details?: Record<string, string[]>;
}