import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { authService } from "@/services/authService"
import type { User, TokenResponse } from "@/services/authService"
import { getAccessToken, setTokens, clearTokens, setStoredUser, getStoredUser } from "@/utils/storage"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: { email: string; password: string }) => Promise<void>
  signup: (data: { email: string; password: string; full_name?: string }) => Promise<void>
  googleLogin: (googleToken: string) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(getStoredUser())
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken()
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
          setStoredUser(currentUser)
        } catch (error) {
          console.warn("Failed to validate existing token:", error)
          clearTokens()
          setUser(null)
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const handleAuthResponse = (response: TokenResponse) => {
    setTokens(response.access_token, response.refresh_token)
    setUser(response.user)
    setStoredUser(response.user)
  }

  const login = async (data: { email: string; password: string }) => {
    const response = await authService.login(data)
    handleAuthResponse(response)
  }

  const signup = async (data: { email: string; password: string; full_name?: string }) => {
    const response = await authService.signup(data)
    handleAuthResponse(response)
  }

  const googleLogin = async (googleToken: string) => {
    const response = await authService.googleAuth(googleToken)
    handleAuthResponse(response)
  }

  const logout = () => {
    clearTokens()
    setUser(null)
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
    setStoredUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        googleLogin,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
