import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = RequestInit & { auth?: boolean };

async function parseError(response: Response): Promise<string> {
  const data = await response.json().catch(() => ({}));
  const detail = (data as { detail?: string | { msg: string }[] }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return "Request failed.";
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = false, headers, ...rest } = options;

  const requestHeaders: HeadersInit = {
    "Content-Type": "application/json",
    ...(headers ?? {}),
  };

  if (auth) {
    const token = getToken();
    if (!token) throw new ApiError("You must be signed in.");
    (requestHeaders as Record<string, string>).Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: requestHeaders,
  });

  if (!response.ok) {
    throw new ApiError(await parseError(response));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type TokenResponse = { access_token: string; token_type: string };
export type User = { id: string; email: string; full_name: string };

export function login(email: string, password: string) {
  return api<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(email: string, password: string, full_name: string) {
  return api<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name }),
  });
}

export function getMe() {
  return api<User>("/api/v1/auth/me", { auth: true });
}

export function triggerOutboundCall(phone_number: string, customer_name: string) {
  return api<{ status: string; data: unknown }>("/api/v1/calls/outbound", {
    method: "POST",
    body: JSON.stringify({ phone_number, customer_name }),
  });
}
