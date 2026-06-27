import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import { clearToken, getToken, setToken } from "@/lib/auth-storage"
import { apiRequest, loginRequest } from "@/lib/api"
import type { User } from "@/types/api"

interface AuthContextValue {
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setAuthToken] = useState<string | null>(getToken())

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      login: async (email, password) => {
        const data = await loginRequest(email, password)
        setToken(data.access_token)
        setAuthToken(data.access_token)
      },
      register: async (email, password, fullName) => {
        await apiRequest<User>(
          "/api/v1/auth/register",
          {
            method: "POST",
            body: JSON.stringify({
              email,
              password,
              full_name: fullName ?? null,
            }),
          },
          false,
        )
        const data = await loginRequest(email, password)
        setToken(data.access_token)
        setAuthToken(data.access_token)
      },
      logout: () => {
        clearToken()
        setAuthToken(null)
      },
    }),
    [token],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
