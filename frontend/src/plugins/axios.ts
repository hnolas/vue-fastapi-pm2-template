import axios from 'axios'
import { useRouter } from 'vue-router'

// API base URL from environment variable or default
const API_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance with common configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include authentication token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Use this function to set up the response interceptor that requires router
export function setupAxiosInterceptors(router: ReturnType<typeof useRouter>) {
  // Add response interceptor to handle authentication errors
  apiClient.interceptors.response.use(
    response => response,
    error => {
      // Redirect to login on unauthorized responses
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
      }
      return Promise.reject(error)
    }
  )
}

export default apiClient