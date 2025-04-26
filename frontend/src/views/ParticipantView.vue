<template>
  <div class="participant-view">
    <div class="page-header mb-4">
      <h1 class="page-title">Participants</h1>
      <button @click="showAddParticipant = true" class="btn btn-primary">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 5v14"></path><path d="M5 12h14"></path>
        </svg>
        <span class="ml-1">Add Participant</span>
      </button>
    </div>

    <div class="card">
      <ParticipantTable />
    </div>

    <!-- Add Participant Modal -->
    <div v-if="showAddParticipant" class="modal-backdrop">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add New Participant</h3>
          <button @click="showAddParticipant = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <ParticipantForm 
            :loading="loading" 
            :error="error"
            @submit="createParticipant" 
            @cancel="showAddParticipant = false" 
          />
        </div>
      </div>
    </div>

    <!-- Edit Participant Modal -->
    <div v-if="showEditParticipant" class="modal-backdrop">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Participant</h3>
          <button @click="showEditParticipant = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <ParticipantForm 
            :participant="selectedParticipant" 
            :loading="loading" 
            :error="error"
            @submit="updateParticipant" 
            @cancel="showEditParticipant = false" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import ParticipantTable from '../components/ParticipantTable.vue'
import ParticipantForm from '../components/ParticipantForm.vue'
import { useParticipantStore } from '../stores/participants'

export default defineComponent({
  name: 'ParticipantView',
  
  components: {
    ParticipantTable,
    ParticipantForm
  },
  
  setup() {
    const participantStore = useParticipantStore()
    
    const showAddParticipant = ref(false)
    const showEditParticipant = ref(false)
    const selectedParticipant = ref(null)
    const loading = ref(false)
    const error = ref('')
    
    const createParticipant = async (participantData: any) => {
      loading.value = true
      error.value = ''
      
      try {
        await participantStore.createParticipant(participantData)
        showAddParticipant.value = false
      } catch (err: any) {
        error.value = err.message || 'Failed to create participant'
      } finally {
        loading.value = false
      }
    }
    
    const updateParticipant = async (participantData: any) => {
      if (!selectedParticipant.value) return
      
      loading.value = true
      error.value = ''
      
      try {
        // @ts-ignore: Object is possibly null
        await participantStore.updateParticipant(selectedParticipant.value.id, participantData)
        showEditParticipant.value = false
      } catch (err: any) {
        error.value = err.message || 'Failed to update participant'
      } finally {
        loading.value = false
      }
    }
    
    return {
      showAddParticipant,
      showEditParticipant,
      selectedParticipant,
      loading,
      error,
      createParticipant,
      updateParticipant
    }
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

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 4px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-body {
  padding: 1rem;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
</style>
