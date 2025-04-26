<template>
  <div id="app">
    <NavBar v-if="showNavBar" />
    <main class="main-content" :class="{ 'with-navbar': showNavBar }">
      <div class="container py-4">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'

export default defineComponent({
  name: 'App',
  
  components: {
    NavBar
  },
  
  setup() {
    const route = useRoute()
    
    // Only show navbar on authenticated routes
    const showNavBar = computed(() => {
      return route.meta.requiresAuth
    })
    
    return {
      showNavBar
    }
  }
})
</script>

<style>
@import './assets/main.css';

html, body {
  height: 100%;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

.main-content.with-navbar {
  padding-top: 1rem;
}

@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
