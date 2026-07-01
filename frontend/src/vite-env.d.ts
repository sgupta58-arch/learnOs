/// <reference types="vite/client" />

/**
 * Environment variable type augmentation.
 *
 * Declares the shape of VITE_ prefixed environment variables
 * for compile-time type checking.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_APP_NAME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}