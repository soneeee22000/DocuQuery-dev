/**
 * Auth API functions.
 */

import type { ApiResponse } from "@/types/api";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types/auth";

import apiClient, { setAccessToken, setRefreshToken } from "./api-client";

/** Register a new user and store tokens. */
export async function registerUser(
  body: RegisterRequest,
): Promise<TokenResponse> {
  const { data } = await apiClient.post<ApiResponse<TokenResponse>>(
    "/auth/register",
    body,
  );
  const tokens = data.data!;
  setAccessToken(tokens.access_token);
  setRefreshToken(tokens.refresh_token);
  return tokens;
}

/** Login and store tokens. */
export async function loginUser(body: LoginRequest): Promise<TokenResponse> {
  const { data } = await apiClient.post<ApiResponse<TokenResponse>>(
    "/auth/login",
    body,
  );
  const tokens = data.data!;
  setAccessToken(tokens.access_token);
  setRefreshToken(tokens.refresh_token);
  return tokens;
}

/** Fetch the current user. */
export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<ApiResponse<User>>("/auth/me");
  return data.data!;
}
