import type { ApiError, ApiResponse } from "@/types/api"
import { clearToken, getToken } from "@/lib/auth-storage"

const API_BASE = import.meta.env.VITE_API_URL ?? ""

export class ApiRequestError extends Error {
  code: string
  status: number

  constructor(message: string, code: string, status: number) {
    super(message)
    this.code = code
    this.status = status
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as ApiResponse<T> | ApiError

  if (!response.ok) {
    const errorPayload = payload as ApiError
    throw new ApiRequestError(
      errorPayload.error?.message ?? "Request failed",
      errorPayload.error?.code ?? "request_failed",
      response.status,
    )
  }

  return (payload as ApiResponse<T>).data
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers = new Headers(options.headers)

  if (auth) {
    const token = getToken()
    if (token) {
      headers.set("Authorization", `Bearer ${token}`)
    }
  }

  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 401 && auth) {
    clearToken()
    if (window.location.pathname !== "/login") {
      window.location.href = "/login"
    }
  }

  return parseResponse<T>(response)
}

export async function loginRequest(email: string, password: string) {
  const body = new URLSearchParams({
    username: email,
    password,
  })

  return apiRequest<{ access_token: string; token_type: string }>(
    "/api/v1/auth/login",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body,
    },
    false,
  )
}
