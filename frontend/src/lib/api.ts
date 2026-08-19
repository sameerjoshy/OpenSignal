import { API_BASE } from "../config";
import type { TokenResponse, User } from "../types";

const TOKEN_KEY = "opensignal_token";
const USER_KEY = "opensignal_user";

export function setSession(token: string, user: User): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const isForm = typeof FormData !== "undefined" && options.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(!isForm ? { "Content-Type": "application/json" } : {}),
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    if (token) {
      clearSession();
      window.location.href = "/login";
    }
    throw new ApiError(401, token ? "Session expired" : "Invalid email or password");
  }

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof body === "object" && body !== null ? (body as { detail?: string }).detail || "Request failed" : String(body);
    throw new ApiError(response.status, message);
  }
  return body as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: "POST", body: data === undefined ? undefined : JSON.stringify(data) }),
  patch: <T>(path: string, data?: unknown) => request<T>(path, { method: "PATCH", body: JSON.stringify(data) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  postForm: <T>(path: string, formData: FormData) =>
    request<T>(path, {
      method: "POST",
      body: formData,
    }),
  download: async (path: string, filename: string): Promise<void> => {
    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}${path}`, { headers });
    if (!response.ok) {
      throw new ApiError(response.status, `Download failed (${response.status})`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
};

export async function exchangeSupabaseToken(accessToken: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/api/v1/auth/exchange", { access_token: accessToken });
}

export async function loginWithPassword(email: string, password: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/api/v1/auth/login", { email, password });
}

export async function signupWithPassword(email: string, password: string, full_name: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/api/v1/auth/signup", { email, password, full_name });
}

export async function fetchMe(): Promise<User> {
  return api.get<User>("/api/v1/auth/me");
}