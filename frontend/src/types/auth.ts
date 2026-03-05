/** User object returned from the API. */
export interface User {
  id: string;
  email: string;
  created_at: string;
}

/** Token pair response from login/register. */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** Login request body. */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Register request body. */
export interface RegisterRequest {
  email: string;
  password: string;
}
