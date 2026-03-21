/**
 * Token validation utilities for JWT authentication
 * Shared between middleware (Edge runtime) and client-side code
 */

/**
 * Validate JWT token structure and expiration
 * @param token - JWT token string
 * @returns true if token is valid and not expired
 */
export function isValidToken(token: string | undefined | null): boolean {
  if (!token) return false;

  // Validate JWT structure: header.payload.signature
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  const [header, payload, signature] = parts;
  if (!header || !payload || !signature) return false;

  // Each part should be a non-trivial base64 string
  if (header.length < 2 || payload.length < 2 || signature.length < 2) return false;

  // Verify payload is valid base64 and contains expected JWT claims
  try {
    const decoded = JSON.parse(atob(payload));
    // Must have an expiration claim
    if (!decoded.exp) return false;
    // Check if token is expired
    const now = Math.floor(Date.now() / 1000);
    if (decoded.exp < now) return false;
  } catch {
    return false;
  }

  return true;
}

/**
 * Decode JWT payload without verification
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeTokenPayload<T = Record<string, unknown>>(token: string): T | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    return JSON.parse(atob(parts[1])) as T;
  } catch {
    return null;
  }
}

/**
 * Get token expiration time in seconds
 * @param token - JWT token string
 * @returns Expiration timestamp (Unix seconds) or null if invalid
 */
export function getTokenExpiration(token: string): number | null {
  const payload = decodeTokenPayload<{ exp?: number }>(token);
  return payload?.exp ?? null;
}

/**
 * Check if token will expire within given seconds
 * @param token - JWT token string
 * @param withinSeconds - Seconds threshold
 * @returns true if token will expire within the threshold
 */
export function isTokenExpiringSoon(token: string, withinSeconds: number = 300): boolean {
  const exp = getTokenExpiration(token);
  if (!exp) return true;
  const now = Math.floor(Date.now() / 1000);
  return (exp - now) <= withinSeconds;
}
