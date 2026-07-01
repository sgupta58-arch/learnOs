/**
 * Environment configuration module.
 *
 * All environment variables are read through this module.
 * Never access `import.meta.env` directly outside this file.
 */

interface EnvConfig {
  apiUrl: string;
  appName: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

function getEnvVar(key: string, fallback: string): string {
  const value = (import.meta.env[key] as string | undefined) ?? fallback;
  return value;
}

export const env: EnvConfig = {
  apiUrl: getEnvVar('VITE_API_URL', 'http://localhost:8000/api/v1'),
  appName: getEnvVar('VITE_APP_NAME', 'LearnOS'),
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;