import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { isSupabaseEnabled, supabase } from "../lib/supabase";
import {
  clearSession,
  exchangeSupabaseToken,
  fetchMe,
  getToken,
  getUser,
  loginWithPassword,
  setSession,
  signupWithPassword,
} from "../lib/api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => getUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        if (isSupabaseEnabled() && supabase) {
          const { data } = await supabase.auth.getSession();
          if (data.session) {
            const token = await exchangeSupabaseToken(data.session.access_token);
            if (!cancelled) setSession(token.access_token, token.user);
            if (!cancelled) setUser(token.user);
          } else if (getToken()) {
            const me = await fetchMe();
            if (!cancelled) setUser(me);
          }
        } else if (getToken()) {
          const me = await fetchMe();
          if (!cancelled) setUser(me);
        }
      } catch {
        clearSession();
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    let token: string;
    let nextUser: User;

    if (isSupabaseEnabled() && supabase) {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error || !data.session) throw new Error(error?.message || "Login failed");
      const exchanged = await exchangeSupabaseToken(data.session.access_token);
      token = exchanged.access_token;
      nextUser = exchanged.user;
    } else {
      const response = await loginWithPassword(email, password);
      token = response.access_token;
      nextUser = response.user;
    }

    setSession(token, nextUser);
    setUser(nextUser);
  }, []);

  const signUp = useCallback(async (email: string, password: string, fullName: string) => {
    if (isSupabaseEnabled() && supabase) {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { full_name: fullName } },
      });
      if (error) throw new Error(error.message);
      // With email confirmation enabled the user must verify before login.
      if (!data.session) {
        throw new Error("Check your email to verify your account, then sign in.");
      }
      const exchanged = await exchangeSupabaseToken(data.session.access_token);
      setSession(exchanged.access_token, exchanged.user);
      setUser(exchanged.user);
    } else {
      const response = await signupWithPassword(email, password, fullName);
      setSession(response.access_token, response.user);
      setUser(response.user);
    }
  }, []);

  const signOut = useCallback(async () => {
    if (isSupabaseEnabled() && supabase) {
      await supabase.auth.signOut();
    }
    clearSession();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const me = await fetchMe();
    setUser(me);
  }, []);

  const value = useMemo(
    () => ({ user, loading, signIn, signUp, signOut, refreshUser }),
    [user, loading, signIn, signUp, signOut, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}