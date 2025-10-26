'use client';

import {createContext, useCallback, useContext, useEffect, useMemo, useState} from 'react';
import {login as loginApi, fetchCurrentUser} from '@/lib/api/auth';

const STORAGE_KEY = 'pii-admin-token';

const AuthContext = createContext(null);

export function AuthProvider({children}) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const storedToken = window.localStorage.getItem(STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }

    let cancelled = false;
    async function loadUser() {
      try {
        const profile = await fetchCurrentUser({token});
        if (!cancelled) {
          setUser(profile);
        }
      } catch (error) {
        console.error('Failed to load user profile', error);
        if (!cancelled) {
          setToken(null);
          if (typeof window !== 'undefined') {
            window.localStorage.removeItem(STORAGE_KEY);
          }
        }
      }
    }

    loadUser();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const login = useCallback(async (credentials) => {
    const result = await loginApi(credentials);
    const accessToken = result?.access_token;
    if (!accessToken) {
      throw new Error('서버에서 토큰을 반환하지 않았습니다.');
    }
    setToken(accessToken);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, accessToken);
    }
    return result;
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      loading,
      login,
      logout
    }),
    [token, user, loading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 AuthProvider 내부에서만 사용할 수 있습니다.');
  }
  return context;
}
