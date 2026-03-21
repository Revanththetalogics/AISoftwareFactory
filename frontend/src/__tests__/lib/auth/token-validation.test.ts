import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  isValidToken,
  decodeTokenPayload,
  getTokenExpiration,
  isTokenExpiringSoon,
} from '@/lib/auth/token-validation';

/**
 * Helper function to create a valid JWT structure
 * Note: These are mock tokens for testing structure validation only
 */
function createMockJWT(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payloadEncoded = btoa(JSON.stringify(payload));
  const signature = btoa('mock-signature-that-is-long-enough');
  return `${header}.${payloadEncoded}.${signature}`;
}

/**
 * Helper to get future timestamp (Unix seconds)
 */
function getFutureTimestamp(secondsFromNow: number): number {
  return Math.floor(Date.now() / 1000) + secondsFromNow;
}

/**
 * Helper to get past timestamp (Unix seconds)
 */
function getPastTimestamp(secondsAgo: number): number {
  return Math.floor(Date.now() / 1000) - secondsAgo;
}

describe('Token Validation', () => {
  describe('isValidToken', () => {
    describe('valid tokens', () => {
      it('returns true for valid JWT with future expiration', () => {
        const token = createMockJWT({ exp: getFutureTimestamp(3600), sub: 'user123' });
        expect(isValidToken(token)).toBe(true);
      });

      it('returns true for token expiring in 1 second', () => {
        const token = createMockJWT({ exp: getFutureTimestamp(1) });
        expect(isValidToken(token)).toBe(true);
      });

      it('returns true for token with additional claims', () => {
        const token = createMockJWT({
          exp: getFutureTimestamp(3600),
          iat: getPastTimestamp(60),
          sub: 'user123',
          role: 'admin',
        });
        expect(isValidToken(token)).toBe(true);
      });
    });

    describe('expired tokens', () => {
      it('returns false for expired JWT', () => {
        const token = createMockJWT({ exp: getPastTimestamp(3600) });
        expect(isValidToken(token)).toBe(false);
      });

      it('returns false for token that expired 1 second ago', () => {
        const token = createMockJWT({ exp: getPastTimestamp(1) });
        expect(isValidToken(token)).toBe(false);
      });

      it('returns false for token with exp = 0', () => {
        const token = createMockJWT({ exp: 0 });
        expect(isValidToken(token)).toBe(false);
      });
    });

    describe('malformed tokens', () => {
      it('returns false for empty string', () => {
        expect(isValidToken('')).toBe(false);
      });

      it('returns false for undefined', () => {
        expect(isValidToken(undefined)).toBe(false);
      });

      it('returns false for null', () => {
        expect(isValidToken(null)).toBe(false);
      });

      it('returns false for string without dots', () => {
        expect(isValidToken('no-dots-here')).toBe(false);
      });

      it('returns false for 2-part string (missing signature)', () => {
        expect(isValidToken('header.payload')).toBe(false);
      });

      it('returns false for 4-part string (too many parts)', () => {
        expect(isValidToken('header.payload.signature.extra')).toBe(false);
      });

      it('returns false for token with empty parts', () => {
        expect(isValidToken('...')).toBe(false);
      });

      it('returns false for token with short parts', () => {
        expect(isValidToken('a.b.c')).toBe(false);
      });

      it('returns false for token with invalid base64 payload', () => {
        const header = btoa(JSON.stringify({ alg: 'HS256' }));
        const invalidPayload = '!!!invalid-base64!!!';
        const signature = btoa('signature');
        expect(isValidToken(`${header}.${invalidPayload}.${signature}`)).toBe(false);
      });

      it('returns false for token with non-JSON payload', () => {
        const header = btoa(JSON.stringify({ alg: 'HS256' }));
        const nonJsonPayload = btoa('this is not json');
        const signature = btoa('signature');
        expect(isValidToken(`${header}.${nonJsonPayload}.${signature}`)).toBe(false);
      });

      it('returns false for token missing exp claim', () => {
        const header = btoa(JSON.stringify({ alg: 'HS256' }));
        const payloadWithoutExp = btoa(JSON.stringify({ sub: 'user123' }));
        const signature = btoa('signature');
        expect(isValidToken(`${header}.${payloadWithoutExp}.${signature}`)).toBe(false);
      });

      it('returns false for random gibberish', () => {
        expect(isValidToken('random.gibberish.here')).toBe(false);
      });
    });
  });

  describe('decodeTokenPayload', () => {
    it('returns decoded payload for valid token', () => {
      const payload = { exp: getFutureTimestamp(3600), sub: 'user123', role: 'admin' };
      const token = createMockJWT(payload);
      
      const decoded = decodeTokenPayload(token);
      expect(decoded).toEqual(payload);
    });

    it('returns null for invalid token structure', () => {
      expect(decodeTokenPayload('invalid')).toBe(null);
    });

    it('returns null for token with invalid base64', () => {
      expect(decodeTokenPayload('header.!!!.signature')).toBe(null);
    });

    it('correctly types the decoded payload', () => {
      interface CustomPayload {
        exp: number;
        userId: string;
        permissions: string[];
        [key: string]: unknown;  // Index signature for compatibility with Record<string, unknown>
      }
      
      const payload: CustomPayload = {
        exp: getFutureTimestamp(3600),
        userId: 'user-456',
        permissions: ['read', 'write'],
      };
      
      const token = createMockJWT(payload);
      const decoded = decodeTokenPayload<CustomPayload>(token);
      
      expect(decoded?.userId).toBe('user-456');
      expect(decoded?.permissions).toEqual(['read', 'write']);
    });
  });

  describe('getTokenExpiration', () => {
    it('returns expiration timestamp for valid token', () => {
      const exp = getFutureTimestamp(3600);
      const token = createMockJWT({ exp });
      
      expect(getTokenExpiration(token)).toBe(exp);
    });

    it('returns null for token without exp', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256' }));
      const payload = btoa(JSON.stringify({ sub: 'user' }));
      const signature = btoa('sig');
      
      expect(getTokenExpiration(`${header}.${payload}.${signature}`)).toBe(null);
    });

    it('returns null for invalid token', () => {
      expect(getTokenExpiration('invalid')).toBe(null);
    });
  });

  describe('isTokenExpiringSoon', () => {
    it('returns false for token expiring in 1 hour (default threshold)', () => {
      const token = createMockJWT({ exp: getFutureTimestamp(3600) });
      expect(isTokenExpiringSoon(token)).toBe(false);
    });

    it('returns true for token expiring in 1 minute (default 5 min threshold)', () => {
      const token = createMockJWT({ exp: getFutureTimestamp(60) });
      expect(isTokenExpiringSoon(token)).toBe(true);
    });

    it('returns true for already expired token', () => {
      const token = createMockJWT({ exp: getPastTimestamp(60) });
      expect(isTokenExpiringSoon(token)).toBe(true);
    });

    it('respects custom threshold', () => {
      const token = createMockJWT({ exp: getFutureTimestamp(600) }); // 10 minutes
      
      expect(isTokenExpiringSoon(token, 300)).toBe(false); // 5 min threshold
      expect(isTokenExpiringSoon(token, 900)).toBe(true);  // 15 min threshold
    });

    it('returns true for invalid token', () => {
      expect(isTokenExpiringSoon('invalid')).toBe(true);
    });

    it('returns true for token without exp', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256' }));
      const payload = btoa(JSON.stringify({ sub: 'user' }));
      const signature = btoa('sig');
      
      expect(isTokenExpiringSoon(`${header}.${payload}.${signature}`)).toBe(true);
    });
  });
});
