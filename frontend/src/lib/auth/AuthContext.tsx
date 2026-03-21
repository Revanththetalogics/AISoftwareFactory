'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { User, LoginResponse } from '@/lib/types';
import { api } from '@/lib/api/client';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (response: LoginResponse) => void;
  logout: () => Promise<void>;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'aifactory_token';
const USER_KEY = 'aifactory_user';
const TOKEN_EXPIRY_KEY = 'aifactory_token_expiry';

/**
 * NOTE: Auth cookies are now httpOnly and set by the backend.
 * The frontend cannot read or set auth_token cookies directly.
 * All cookie operations are handled server-side for security.
 */

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initAuth = () => {
      try {
        const token = localStorage.getItem(TOKEN_KEY);
        const userData = localStorage.getItem(USER_KEY);
        const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);

        console.log('Auth Initialization:', {
          hasToken: !!token,
          hasUser: !!userData,
          hasExpiry: !!expiry,
          expiry: expiry ? new Date(expiry).toISOString() : null,
          now: new Date().toISOString()
        });

        if (token && userData && expiry) {
          const expiryDate = new Date(expiry);
          if (expiryDate > new Date()) {
            const parsedUser = JSON.parse(userData);
            console.log('Auth: User authenticated from storage', parsedUser);
            setUser(parsedUser);
            // Sync token with API client for Authorization header fallback
            api.setToken(token);
          } else {
            console.log('Auth: Token expired, clearing storage');
            // Token expired, clear storage
            // Note: httpOnly cookies will be handled by backend on next request
            api.setToken(null);
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            localStorage.removeItem(TOKEN_EXPIRY_KEY);
            setUser(null);
          }
        } else {
          console.log('Auth: No valid credentials found');
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback((response: LoginResponse) => {
    const expiryDate = new Date();
    expiryDate.setSeconds(expiryDate.getSeconds() + response.expires_in);

    // Store in localStorage for client-side state
    localStorage.setItem(TOKEN_KEY, response.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryDate.toISOString());

    // Sync token with API client for Authorization header fallback
    api.setToken(response.access_token);

    // Note: httpOnly cookies are set by the backend response
    // The frontend cannot and should not try to set auth cookies

    setUser(response.user);
  }, []);

  const logout = useCallback(async () => {
    // Call backend logout endpoint to clear httpOnly cookies
    try {
      await api.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local cleanup even if API call fails
    }

    // Clear localStorage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
    
    // Clear token from API client
    api.setToken(null);
    
    setUser(null);
  }, []);

  const getToken = useCallback(() => {
    return localStorage.getItem(TOKEN_KEY);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
