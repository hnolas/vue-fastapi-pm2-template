<template>
  <nav class="navbar">
    <div class="container">
      <div class="navbar-logo">
        <router-link to="/" class="logo-link">
          <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
          </div>
          <span class="logo-text">PMI</span>
        </router-link>
      </div>
      
      <div class="navbar-links">
        <router-link to="/" class="nav-link" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <span>Dashboard</span>
        </router-link>
        
        <router-link to="/participants" class="nav-link" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <span>Participants</span>
        </router-link>
        
        <router-link to="/messages" class="nav-link" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>Messages</span>
        </router-link>
        
        <router-link to="/fitbit" class="nav-link" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 20V10"></path>
            <path d="M12 20V4"></path>
            <path d="M6 20v-6"></path>
          </svg>
          <span>Fitbit</span>
        </router-link>
      </div>
      
      <div class="navbar-profile">
        <button class="profile-button" @click="showLogoutMenu = !showLogoutMenu">
          <div class="profile-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <span class="profile-name">Researcher</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        
        <div v-if="showLogoutMenu" class="logout-menu">
          <button class="logout-button" @click="logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'NavBar',
  
  setup() {
    const router = useRouter()
    const showLogoutMenu = ref(false)
    
    const logout = () => {
      // Clear the token from local storage
      localStorage.removeItem('token')
      
      // Close the logout menu
      showLogoutMenu.value = false
      
      // Redirect to the login page
      router.push('/login')
    }
    
    // Close the logout menu when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.profile-button') && !target.closest('.logout-menu')) {
        showLogoutMenu.value = false
      }
    }
    
    // Add and remove event listener
    window.addEventListener('click', handleClickOutside)
    
    return {
      showLogoutMenu,
      logout
    }
  }
})
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 0.75rem 0;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--dark-color);
  text-decoration: none;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--primary-color);
  border-radius: 8px;
  margin-right: 0.75rem;
  color: white;
}

.navbar-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  color: var(--text-color);
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-link svg {
  margin-right: 0.5rem;
}

.nav-link:hover {
  background-color: var(--light-color);
  text-decoration: none;
}

.nav-link.active {
  background-color: var(--light-color);
  color: var(--primary-color);
  font-weight: 500;
}

.navbar-profile {
  position: relative;
}

.profile-button {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: var(--border-radius);
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.profile-button:hover {
  background-color: var(--light-color);
}

.profile-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--light-color);
  border-radius: 50%;
  margin-right: 0.75rem;
}

.profile-name {
  margin-right: 0.5rem;
  font-weight: 500;
}

.logout-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-top: 0.5rem;
  min-width: 120px;
  z-index: 100;
}

.logout-button {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: var(--light-color);
}

.logout-button svg {
  margin-right: 0.5rem;
  color: var(--danger-color);
}

@media (max-width: 768px) {
  .nav-link span {
    display: none;
  }
  
  .nav-link svg {
    margin-right: 0;
  }
  
  .profile-name {
    display: none;
  }
  
  .profile-avatar {
    margin-right: 0;
  }
}
</style>
