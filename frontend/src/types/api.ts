/** Standard API response wrapper. */
export interface ApiResponse<T> {
  data: T | null;
  error: ErrorDetail | null;
  meta: Record<string, unknown>;
}

/** Error detail in API responses. */
export interface ErrorDetail {
  code: string;
  message: string;
}
