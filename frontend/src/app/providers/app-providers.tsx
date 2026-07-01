import type { ReactNode } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/features/auth/context/auth-context';
import { queryClient } from '@/lib/query-client';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Application providers wrapper.
 *
 * Composes all global providers needed by the application.
 * Designed to be extensible — add new providers here without
 * restructuring the component tree.
 *
 * Current providers:
 * - QueryClientProvider (TanStack Query)
 * - AuthProvider (authentication state)
 *
 * Future providers:
 * - ThemeProvider
 * - ToastProvider
 */
export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
}