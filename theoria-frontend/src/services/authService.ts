import { apiFetch } from "@/services/api"

export interface User {
  id: number
  email: string
  full_name?: string
  avatar_url?: string
  auth_provider: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export const authService = {
  async signup(data: { email: string; password: string; full_name?: string }): Promise<TokenResponse> {
    return apiFetch<TokenResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
      requiresAuth: false,
    })
  },

  async login(data: { email: string; password: string }): Promise<TokenResponse> {
    return apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
      requiresAuth: false,
    })
  },

  async googleAuth(token: string): Promise<TokenResponse> {
    return apiFetch<TokenResponse>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ token }),
      requiresAuth: false,
    })
  },

  async getCurrentUser(): Promise<User> {
    return apiFetch<User>("/users/me", {
      method: "GET",
      requiresAuth: true,
    })
  },

  async updateProfile(data: { full_name?: string; avatar_url?: string; password?: string }): Promise<User> {
    return apiFetch<User>("/users/me", {
      method: "PUT",
      body: JSON.stringify(data),
      requiresAuth: true,
    })
  },
}
