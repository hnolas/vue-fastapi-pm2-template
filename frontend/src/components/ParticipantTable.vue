<template>
  <div class="participant-table">
    <div class="card-header mb-3">
      <h2 class="card-title">Participants</h2>
      <div class="flex gap-2">
        <button @click="refreshParticipants" class="btn btn-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 2v4h-4"></path><path d="M4 11v-4h4"></path>
            <path d="M20 22v-4h-4"></path><path d="M4 13v4h4"></path>
            <path d="M22 16.92v1.08a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.63A2 2 0 0 1 4.11 2h1.08a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L6.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
          <span class="ml-1">Refresh</span>
        </button>
        <button @click="showAddParticipant = true" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14"></path><path d="M5 12h14"></path>
          </svg>
          <span class="ml-1">Add Participant</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-4 grid grid-cols-3 gap-3">
      <div class="form-group">
        <label for="activeFilter" class="form-label">Status</label>
        <select id="activeFilter" v-model="filters.active" class="form-control">
          <option :value="null">All</option>
          <option :value="true">Active</option>
          <option :value="false">Inactive</option>
        </select>
      </div>
      <div class="form-group">
        <label for="studyGroupFilter" class="form-label">Study Group</label>
        <select id="studyGroupFilter" v-model="filters.studyGroup" class="form-control">
          <option :value="null">All</option>
          <option v-for="group in uniqueStudyGroups" :key="group" :value="group">
            {{ group }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="searchFilter" class="form-label">Search</label>
        <input 
          id="searchFilter" 
          v-model="filters.search" 
          type="text" 
          class="form-control" 
          placeholder="Search by PID or name"
        >
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner"></div>
      <p class="mt-2">Loading participants...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      <p>{{ error }}</p>
      <button @click="refreshParticipants" class="btn btn-outline mt-2">Try Again</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="!filteredParticipants.length" class="text-center p-4">
      <p class="mb-3">No participants found.</p>
      <button @click="showAddParticipant = true" class="btn btn-primary">
        Add Your First Participant
      </button>
    </div>

    <!-- Table view -->
    <div v-else class="table-responsive">
      <table class="table">
        <thead>
          <tr>
            <th>PID</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Study Group</th>
            <th>SMS Window</th>
            <th>Start Date</th>
            <th>Status</th>
            <th>Fitbit</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="participant in filteredParticipants" :key="participant.id">
            <td>{{ participant.pid }}</td>
            <td>{{ participant.friendly_name || '-' }}</td>
            <td>{{ participant.phone_number }}</td>
            <td>
              <span class="badge badge-secondary">{{ participant.study_group }}</span>
            </td>
            <td>
              <span v-if="participant.sms_window_start && participant.sms_window_end">
                {{ formatTime(participant.sms_window_start) }} - {{ formatTime(participant.sms_window_end) }}
              </span>
              <span v-else>-</span>
            </td>
            <td>{{ participant.start_date || '-' }}</td>
            <td>
              <span class="badge" :class="participant.active ? 'badge-success' : 'badge-secondary'">
                {{ participant.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span v-if="participant.fitbit_connected" class="badge badge-primary">Connected</span>
              <span v-else-if="participant.fitbit_registration_requested" class="badge badge-warning">Pending</span>
              <span v-else>-</span>
            </td>
            <td>
              <div class="flex gap-2">
                <button 
                  @click="editParticipant(participant)" 
                  title="Edit" 
                  class="btn btn-outline btn-sm btn-icon"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button
                  v-if="!participant.fitbit_connected && !participant.fitbit_registration_requested"
                  @click="requestFitbitRegistration(participant)"
                  title="Request Fitbit Registration"
                  class="btn btn-outline btn-sm btn-icon"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
                  </svg>
                </button>
                <button
                  @click="confirmDeleteParticipant(participant)"
                  title="Delete"
                  class="btn btn-outline btn-sm btn-icon text-danger"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Participant Modal -->
    <div v-if="showAddParticipant || showEditParticipant" class="modal-backdrop">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ showEditParticipant ? 'Edit Participant' : 'Add New Participant' }}</h3>
          <button @click="closeModals" class="btn-close">×</button>
        </div>
        <form @submit.prevent="submitParticipant">
          <div class="modal-body">
            <div class="form-group">
              <label for="pid" class="form-label">Participant ID (PID)</label>
              <input 
                id="pid" 
                v-model="participantForm.pid" 
                type="text" 
                class="form-control" 
                required
                :disabled="showEditParticipant"
              >
            </div>
            <div class="form-group">
              <label for="friendly_name" class="form-label">Friendly Name</label>
              <input 
                id="friendly_name" 
                v-model="participantForm.friendly_name" 
                type="text" 
                class="form-control"
                placeholder="For %F token substitution in messages"
              >
            </div>
            <div class="form-group">
              <label for="phone_number" class="form-label">Phone Number</label>
              <input 
                id="phone_number" 
                v-model="participantForm.phone_number" 
                type="tel" 
                class="form-control" 
                required
                placeholder="+1234567890"
              >
            </div>
            <div class="form-group">
              <label for="study_group" class="form-label">Study Group / Bucket</label>
              <input 
                id="study_group" 
                v-model="participantForm.study_group" 
                type="text" 
                class="form-control" 
                required
              >
            </div>
            <div class="form-group">
              <label for="start_date" class="form-label">Start Date</label>
              <input 
                id="start_date" 
                v-model="participantForm.start_date" 
                type="date" 
                class="form-control"
              >
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="form-group">
                <label for="sms_window_start" class="form-label">SMS Window Start</label>
                <input 
                  id="sms_window_start" 
                  v-model="participantForm.sms_window_start" 
                  type="time" 
                  class="form-control"
                >
              </div>
              <div class="form-group">
                <label for="sms_window_end" class="form-label">SMS Window End</label>
                <input 
                  id="sms_window_end" 
                  v-model="participantForm.sms_window_end" 
                  type="time" 
                  class="form-control"
                >
              </div>
            </div>
            <div class="form-group">
              <label for="timezone_offset" class="form-label">Timezone Offset (minutes from UTC)</label>
              <input 
                id="timezone_offset" 
                v-model="participantForm.timezone_offset" 
                type="number" 
                class="form-control"
                placeholder="e.g. -300 for EST"
              >
              <small class="text-muted">
                EST: -300, CST: -360, MST: -420, PST: -480
              </small>
            </div>
            <div class="form-group">
              <div class="form-check">
                <input 
                  id="active" 
                  v-model="participantForm.active" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="active" class="form-check-label">Active</label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModals" class="btn btn-outline">Cancel</button>
            <button type="submit" class="btn btn-primary">
              {{ showEditParticipant ? 'Update' : 'Add' }} Participant
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-backdrop">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="showDeleteConfirmation = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete participant {{ participantToDelete?.pid }}?</p>
          <p class="text-danger">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteConfirmation = false" class="btn btn-outline">Cancel</button>
          <button @click="deleteParticipant" class="btn btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useParticipantStore } from '../stores/participants'

export default defineComponent({
  name: 'ParticipantTable',
  
  setup() {
    const participantStore = useParticipantStore()
    
    const showAddParticipant = ref(false)
    const showEditParticipant = ref(false)
    const showDeleteConfirmation = ref(false)
    const participantToDelete = ref(null)
    
    const participantForm = ref({
      pid: '',
      friendly_name: '',
      phone_number: '',
      study_group: '',
      start_date: '',
      sms_window_start: '',
      sms_window_end: '',
      timezone_offset: 0,
      active: true
    })
    
    const filters = ref({
      active: null,
      studyGroup: null,
      search: ''
    })
    
    const loading = computed(() => participantStore.loading)
    const error = computed(() => participantStore.error)
    
    const uniqueStudyGroups = computed(() => {
      const groups = new Set(participantStore.participants.map(p => p.study_group))
      return Array.from(groups)
    })
    
    const filteredParticipants = computed(() => {
      let result = [...participantStore.participants]
      
      // Filter by active status
      if (filters.value.active !== null) {
        result = result.filter(p => p.active === filters.value.active)
      }
      
      // Filter by study group
      if (filters.value.studyGroup) {
        result = result.filter(p => p.study_group === filters.value.studyGroup)
      }
      
      // Filter by search term
      if (filters.value.search) {
        const searchTerm = filters.value.search.toLowerCase()
        result = result.filter(p => 
          p.pid.toLowerCase().includes(searchTerm) || 
          (p.friendly_name && p.friendly_name.toLowerCase().includes(searchTerm))
        )
      }
      
      return result
    })
    
    // Fetch participants on component mount
    onMounted(() => {
      refreshParticipants()
    })
    
    const refreshParticipants = async () => {
      await participantStore.fetchParticipants()
    }
    
    const formatTime = (timeString: string) => {
      try {
        // Convert "HH:MM:SS" to "HH:MM AM/PM"
        const [hours, minutes] = timeString.split(':')
        const hour = parseInt(hours)
        const ampm = hour >= 12 ? 'PM' : 'AM'
        const hour12 = hour % 12 || 12
        return `${hour12}:${minutes} ${ampm}`
      } catch (e) {
        return timeString
      }
    }
    
    const closeModals = () => {
      showAddParticipant.value = false
      showEditParticipant.value = false
      resetForm()
    }
    
    const resetForm = () => {
      participantForm.value = {
        pid: '',
        friendly_name: '',
        phone_number: '',
        study_group: '',
        start_date: '',
        sms_window_start: '',
        sms_window_end: '',
        timezone_offset: 0,
        active: true
      }
    }
    
    const editParticipant = (participant: any) => {
      participantForm.value = {
        pid: participant.pid,
        friendly_name: participant.friendly_name || '',
        phone_number: participant.phone_number,
        study_group: participant.study_group,
        start_date: participant.start_date || '',
        sms_window_start: participant.sms_window_start || '',
        sms_window_end: participant.sms_window_end || '',
        timezone_offset: participant.timezone_offset || 0,
        active: participant.active
      }
      
      showEditParticipant.value = true
    }
    
    const submitParticipant = async () => {
      try {
        if (showEditParticipant.value) {
          // Find the participant ID based on PID
          const participant = participantStore.participants.find(p => p.pid === participantForm.value.pid)
          if (participant) {
            await participantStore.updateParticipant(participant.id, participantForm.value)
          }
        } else {
          await participantStore.createParticipant(participantForm.value)
        }
        
        closeModals()
        await refreshParticipants()
      } catch (error) {
        console.error('Error submitting participant:', error)
      }
    }
    
    const confirmDeleteParticipant = (participant: any) => {
      participantToDelete.value = participant
      showDeleteConfirmation.value = true
    }
    
    const deleteParticipant = async () => {
      if (participantToDelete.value) {
        await participantStore.deleteParticipant(participantToDelete.value.id)
        showDeleteConfirmation.value = false
        participantToDelete.value = null
        await refreshParticipants()
      }
    }
    
    const requestFitbitRegistration = async (participant: any) => {
      try {
        await participantStore.requestFitbitRegistration(participant.id)
        await refreshParticipants()
      } catch (error) {
        console.error('Error requesting Fitbit registration:', error)
      }
    }
    
    return {
      loading,
      error,
      participants: participantStore.participants,
      filteredParticipants,
      uniqueStudyGroups,
      showAddParticipant,
      showEditParticipant,
      participantForm,
      showDeleteConfirmation,
      participantToDelete,
      filters,
      refreshParticipants,
      formatTime,
      closeModals,
      editParticipant,
      submitParticipant,
      confirmDeleteParticipant,
      deleteParticipant,
      requestFitbitRegistration
    }
  }
})
</script>

<style scoped>
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

.modal-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.table-responsive {
  overflow-x: auto;
}

.form-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-check-input {
  width: 1rem;
  height: 1rem;
}

.spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 3px solid var(--primary-color);
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.text-danger {
  color: var(--danger-color);
}

.text-muted {
  color: var(--text-light);
  font-size: 0.75rem;
}
</style>
