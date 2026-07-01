/**
 * Token storage utility.
 *
 * Centralizes all JWT storage operations.
 * Never access localStorage directly outside this module.
 * This abstraction allows swapping storage mechanisms (e.g., httpOnly cookies, sessionStorage)
 * without changing any other code.
 */

const TOKEN_KEY = 'learnos_access_token';

export const tokenStorage = {
  /** Save JWT to persistent storage. */
  set(token: string): void {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch {
      // localStorage may be unavailable in some environments (private browsing, SSR)
      // Fail silently — auth will simply not persist across refreshes.
    }
  },

  /** Read JWT from persistent storage. Returns null if no token exists. */
  get(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },

  /** Remove JWT from persistent storage. */
  remove(): void {
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      // Fail silently.
    }
  },
};