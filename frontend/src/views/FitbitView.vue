<template>
  <div class="fitbit-view">
    <div class="page-header mb-4">
      <h1 class="page-title">Fitbit Integration</h1>
    </div>

    <FitbitRegistration />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import FitbitRegistration from '../components/FitbitRegistration.vue'

export default defineComponent({
  name: 'FitbitView',
  
  components: {
    FitbitRegistration
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-color);
}
</style>
