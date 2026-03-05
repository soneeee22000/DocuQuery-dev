/**
 * Axios API client with auth interceptor.
 *
 * Attaches access token to requests and attempts
 * silent refresh on 401 responses.
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "docuquery_refresh_token";

let accessToken: string | null = null;

/** Set the in-memory access token. */
export function setAccessToken(token: string | null): void {
  accessToken = token;
}

/** Get the current access token. */
export function getAccessToken(): string | null {
  return accessToken;
}

/** Store refresh token in localStorage. */
export function setRefreshToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/** Get refresh token from localStorage. */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/** Clear all auth tokens. */
export function clearTokens(): void {
  accessToken = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

/** Attach access token to outgoing requests. */
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

/** On 401, attempt to refresh the token and retry. */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken },
          );
          const tokens = data.data;
          setAccessToken(tokens.access_token);
          setRefreshToken(tokens.refresh_token);

          originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
          return apiClient(originalRequest);
        } catch {
          clearTokens();
        }
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
