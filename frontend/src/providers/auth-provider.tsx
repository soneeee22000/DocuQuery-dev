"use client";

/**
 * Auth context provider.
 *
 * Stores user state, handles login/register/logout,
 * and attempts token refresh on mount.
 */

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  clearTokens,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "@/lib/api-client";
import { getCurrentUser, loginUser, registerUser } from "@/lib/auth";
import type { LoginRequest, RegisterRequest } from "@/types/auth";
import type { User } from "@/types/auth";

import apiClient from "@/lib/api-client";

export interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (body: LoginRequest) => Promise<void>;
  register: (body: RegisterRequest) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /** Try to restore session from refresh token on mount. */
  useEffect(() => {
    const restore = async () => {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        setIsLoading(false);
        return;
      }

      try {
        const { data } = await apiClient.post("/auth/refresh", {
          refresh_token: refreshToken,
        });
        const tokens = data.data;
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);

        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    restore();
  }, []);

  const login = useCallback(async (body: LoginRequest) => {
    await loginUser(body);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }, []);

  const register = useCallback(async (body: RegisterRequest) => {
    await registerUser(body);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, login, register, logout }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
