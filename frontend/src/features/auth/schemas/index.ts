import { z } from 'zod';

/**
 * Login form validation schema.
 *
 * Rules mirror backend:
 * - Email must be valid format
 * - Password is required
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Registration form validation schema.
 *
 * Rules mirror backend UserCreateSchema:
 * - full_name: min 1, max 255
 * - email: valid email format
 * - password: min 8, max 128
 */
export const registerSchema = z.object({
  full_name: z
    .string()
    .min(1, 'Full name is required')
    .max(255, 'Full name must be 255 characters or fewer'),
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be 128 characters or fewer'),
  confirmPassword: z
    .string()
    .min(1, 'Please confirm your password'),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  },
);

export type RegisterFormData = z.infer<typeof registerSchema>;