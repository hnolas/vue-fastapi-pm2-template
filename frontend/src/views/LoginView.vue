<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
          </div>
          <h1 class="login-title">Participant Management Interface</h1>
        </div>
        
        <form @submit.prevent="submitLogin" class="login-form">
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input 
              id="username" 
              v-model="username" 
              type="text" 
              class="form-control" 
              required 
              placeholder="Enter username"
              autocomplete="username"
            >
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              class="form-control" 
              required 
              placeholder="Enter password"
              autocomplete="current-password"
            >
          </div>
          
          <div v-if="error" class="alert alert-danger mt-3">
            {{ error }}
          </div>
          
          <button type="submit" class="btn btn-primary w-full mt-4" :disabled="loading">
            <span v-if="loading">Logging in...</span>
            <span v-else>Login</span>
          </button>
        </form>
        
        <div class="login-info mt-4">
          <p>Default credentials:</p>
          <p>Username: <strong>researcher</strong></p>
          <p>Password: <strong>password</strong></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { LoginCredentials } from '../types/auth'

export default defineComponent({
  name: 'LoginView',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    
    // Computed properties from the auth store
    const loading = computed(() => authStore.loading)
    const error = computed(() => authStore.error)
    
    const submitLogin = async () => {
      const credentials: LoginCredentials = {
        username: username.value,
        password: password.value
      }
      
      const result = await authStore.login(credentials)
      
      if (result) {
        // Redirect to home page on successful login
        router.push('/')
      }
    }
    
    return {
      username,
      password,
      loading,
      error,
      submitLogin
    }
  }
})
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 1rem;
}

.login-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background-color: var(--primary-color);
  border-radius: 16px;
  margin-bottom: 1rem;
  color: white;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-color);
}

.login-form {
  margin-bottom: 1.5rem;
}

.login-info {
  padding: 1rem;
  background-color: var(--light-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
}

.login-info p {
  margin: 0.25rem 0;
}
</style>
