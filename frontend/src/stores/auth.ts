import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../plugins/axios'
import { Token, LoginCredentials, User } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Check if the user is logged in
  const isLoggedIn = (): boolean => {
    return !!token.value
  }
  
  // Login user
  const login = async (credentials: LoginCredentials): Promise<Token | null> => {
    loading.value = true
    error.value = null
    
    try {
      // Create URLSearchParams for token request (OAuth2 requires x-www-form-urlencoded format)
      const params = new URLSearchParams()
      params.append('username', credentials.username)
      params.append('password', credentials.password)
      
      // Make token request with correct content-type
      const response = await apiClient.post<Token>('/auth/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      // Store token in local storage and state
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      
      return response.data
    } catch (err: any) {
      console.error('Login error:', err)
      if (err.response?.status === 401) {
        error.value = 'Invalid username or password'
      } else {
        error.value = 'Login failed. Please try again.'
      }
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Logout user
  const logout = (): void => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
  
  return {
    token,
    user,
    loading,
    error,
    isLoggedIn,
    login,
    logout
  }
})