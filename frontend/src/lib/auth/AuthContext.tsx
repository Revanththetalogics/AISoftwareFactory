'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { User, LoginResponse } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (response: LoginResponse) => void;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'aifactory_token';
const USER_KEY = 'aifactory_user';
const TOKEN_EXPIRY_KEY = 'aifactory_token_expiry';

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

        if (token && userData && expiry) {
          const expiryDate = new Date(expiry);
          if (expiryDate > new Date()) {
            setUser(JSON.parse(userData));
          } else {
            // Token expired, clear storage
            logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
    initAuth();
  }, []);

  const login = useCallback((response: LoginResponse) => {
    const expiryDate = new Date();
    expiryDate.setSeconds(expiryDate.getSeconds() + response.expires_in);

    localStorage.setItem(TOKEN_KEY, response.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryDate.toISOString());

    setUser(response.user);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
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
