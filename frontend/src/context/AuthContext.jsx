import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getCurrentUser, loginUser, registerUser, updateUserProfile } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!token);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function bootstrap() {
      if (!token) return;
      try {
        const me = await getCurrentUser(token);
        if (isMounted) setUser(me);
      } catch (e) {
        if (isMounted) {
          console.warn('Auth bootstrap failed:', e?.message);
          localStorage.removeItem('token');
          setToken(null);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    bootstrap();
    return () => { isMounted = false; };
  }, [token]);

  const value = useMemo(() => ({
    user,
    token,
    loading,
    error,
    async refreshUser() {
      if (!token) return null;
      const me = await getCurrentUser(token);
      setUser(me);
      return me;
    },
    async updateProfile(payload) {
      if (!token) throw new Error('Not authenticated');
      await updateUserProfile(token, payload);
      const me = await getCurrentUser(token);
      setUser(me);
      return me;
    },
    async login(email, password) {
      setError(null);
      const { token: newToken, user: maybeUser } = await loginUser(email, password);
      localStorage.setItem('token', newToken);
      setToken(newToken);
      if (maybeUser) setUser(maybeUser);
      // If backend didn't return user, try to fetch it
      if (!maybeUser) {
        try {
          const me = await getCurrentUser(newToken);
          setUser(me);
        } catch (e) {
          // non-fatal
        }
      }
    },
    async register(email, password) {
      setError(null);
      return await registerUser(email, password);
    },
    logout() {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    }
  }), [user, token, loading, error]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}


