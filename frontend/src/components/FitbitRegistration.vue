<template>
  <div class="fitbit-registration">
    <div class="card">
      <div class="card-header mb-3">
        <h2 class="card-title">Fitbit Wearable Registration Form for Researchs</h2>
        <div class="flex gap-2">
          <button @click="refreshFitbitData" class="btn btn-outline">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 4v6h6"></path><path d="M23 20v-6h-6"></path>
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
            </svg>
            <span class="ml-1">Refresh</span>
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center p-4">
        <div class="spinner">Loading...</div>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="alert alert-danger">
        <p>{{ error }}</p>
        <button @click="refreshFitbitData" class="btn btn-outline mt-2">Try Again</button>
      </div>

      <!-- Fitbit authorization dashboard -->
      <div v-else>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="card">
            <h3 class="text-lg font-medium mb-2">Registration Requests</h3>
            <p class="mb-2">
              {{ pendingCount }} of {{ totalParticipants }} participants pending Fitbit registration
            </p>
            <div class="progress mb-3">
              <div 
                class="progress-bar" 
                :style="{width: `${(connectedCount / totalParticipants) * 100}%`}" 
              ></div>
            </div>
            <button @click="fetchParticipantData" class="btn btn-outline btn-sm">Refresh Status</button>
          </div>

          <div class="card">
            <h3 class="text-lg font-medium mb-2">Fitbit Data Collection</h3>
            <p class="mb-2">Last sync: {{ lastSyncDate || 'Never' }}</p>
            <div class="flex gap-2">
              <button 
                @click="triggerDataFetch" 
                class="btn btn-primary btn-sm"
                :disabled="fetchingData"
              >
                <span v-if="fetchingData">Syncing...</span>
                <span v-else>Sync Fitbit Data</span>
              </button>
              <button @click="exportData" class="btn btn-outline btn-sm">Export to Dropbox</button>
            </div>
          </div>
        </div>

        <!-- Participant Fitbit status table -->
        <div class="mb-4">
          <h3 class="text-lg font-medium mb-3">Participant Fitbit Status</h3>
          
          <!-- Filter controls -->
          <div class="flex gap-3 mb-3">
            <div class="form-group flex-1">
              <input 
                v-model="search" 
                type="text" 
                class="form-control" 
                placeholder="Search by PID or name"
              >
            </div>
            <div class="form-group">
              <select v-model="statusFilter" class="form-control">
                <option value="all">All Statuses</option>
                <option value="connected">Connected</option>
                <option value="pending">Pending</option>
                <option value="not-requested">Not Requested</option>
              </select>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>PID</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Last Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="participant in filteredParticipants" :key="participant.id">
                  <td>{{ participant.pid }}</td>
                  <td>{{ participant.friendly_name || '-' }}</td>
                  <td>
                    <span 
                      class="badge" 
                      :class="getFitbitStatusClass(participant)"
                    >
                      {{ getFitbitStatus(participant) }}
                    </span>
                  </td>
                  <td>{{ formatDate(participant.updated_at) }}</td>
                  <td>
                    <div class="flex gap-2">
                      <button 
                        v-if="!participant.fitbit_connected && !participant.fitbit_registration_requested"
                        @click="requestRegistration(participant.id)"
                        class="btn btn-sm btn-outline"
                        :disabled="requesting"
                      >
                        Request Registration
                      </button>
                      <button 
                        v-if="participant.fitbit_registration_requested && !participant.fitbit_connected"
                        @click="getRegistrationLink(participant.pid)"
                        class="btn btn-sm btn-primary"
                      >
                        Get Link
                      </button>
                      <button 
                        v-if="participant.fitbit_connected"
                        @click="syncParticipantData(participant.id)"
                        class="btn btn-sm btn-outline"
                        :disabled="fetchingData"
                      >
                        Sync Data
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Registration link modal -->
        <div v-if="showLinkModal" class="modal-backdrop">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Fitbit Registration Link</h3>
              <button @click="showLinkModal = false" class="btn-close">×</button>
            </div>
            <div class="modal-body">
              <p class="mb-3">Share this link with the participant to connect their Fitbit account:</p>
              <div class="registration-link">
                {{ registrationLink }}
              </div>
              <div class="text-center mt-3">
                <button @click="copyLink" class="btn btn-primary">
                  {{ linkCopied ? 'Copied!' : 'Copy Link' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useFitbitStore } from '../stores/fitbit'
import { useParticipantStore } from '../stores/participants'

export default defineComponent({
  name: 'FitbitRegistration',
  
  setup() {
    const fitbitStore = useFitbitStore()
    const participantStore = useParticipantStore()
    
    const search = ref('')
    const statusFilter = ref('all')
    const showLinkModal = ref(false)
    const registrationLink = ref('')
    const linkCopied = ref(false)
    const lastSyncDate = ref('')
    const fetchingData = ref(false)
    const requesting = ref(false)
    
    onMounted(async () => {
      refreshFitbitData()
    })
    
    const refreshFitbitData = async () => {
      if (participantStore.participants.length === 0) {
        await participantStore.fetchParticipants()
      }
      await fitbitStore.fetchTokens()
    }
    
    const fetchParticipantData = async () => {
      await participantStore.fetchParticipants()
    }
    
    const triggerDataFetch = async () => {
      fetchingData.value = true
      try {
        await fitbitStore.triggerDataFetch()
        lastSyncDate.value = new Date().toLocaleString()
      } catch (error) {
        console.error('Error fetching Fitbit data:', error)
      } finally {
        fetchingData.value = false
      }
    }
    
    const syncParticipantData = async (participantId: number) => {
      fetchingData.value = true
      try {
        await fitbitStore.triggerDataFetch(participantId)
      } catch (error) {
        console.error('Error syncing participant data:', error)
      } finally {
        fetchingData.value = false
      }
    }
    
    const exportData = async () => {
      try {
        await fitbitStore.exportData()
      } catch (error) {
        console.error('Error exporting data:', error)
      }
    }
    
    const requestRegistration = async (participantId: number) => {
      requesting.value = true
      try {
        await fitbitStore.requestRegistration(participantId)
        await participantStore.fetchParticipants()
      } catch (error) {
        console.error('Error requesting registration:', error)
      } finally {
        requesting.value = false
      }
    }
    
    const getRegistrationLink = (pid: string) => {
      const baseUrl = window.location.origin
      registrationLink.value = `${baseUrl}/api/fitbit/login?pid=${pid}`
      showLinkModal.value = true
      linkCopied.value = false
    }
    
    const copyLink = () => {
      navigator.clipboard.writeText(registrationLink.value)
      linkCopied.value = true
      setTimeout(() => {
        linkCopied.value = false
      }, 2000)
    }
    
    const formatDate = (dateString: string) => {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date)
    }
    
    const getFitbitStatus = (participant: any) => {
      if (participant.fitbit_connected) {
        return 'Connected'
      } else if (participant.fitbit_registration_requested) {
        return 'Pending'
      } else {
        return 'Not Requested'
      }
    }
    
    const getFitbitStatusClass = (participant: any) => {
      if (participant.fitbit_connected) {
        return 'badge-success'
      } else if (participant.fitbit_registration_requested) {
        return 'badge-warning'
      } else {
        return 'badge-secondary'
      }
    }
    
    const filteredParticipants = computed(() => {
      let result = [...participantStore.participants]
      
      // Apply search filter
      if (search.value) {
        const searchTerm = search.value.toLowerCase()
        result = result.filter(p => 
          p.pid.toLowerCase().includes(searchTerm) || 
          (p.friendly_name && p.friendly_name.toLowerCase().includes(searchTerm))
        )
      }
      
      // Apply status filter
      if (statusFilter.value !== 'all') {
        if (statusFilter.value === 'connected') {
          result = result.filter(p => p.fitbit_connected)
        } else if (statusFilter.value === 'pending') {
          result = result.filter(p => p.fitbit_registration_requested && !p.fitbit_connected)
        } else if (statusFilter.value === 'not-requested') {
          result = result.filter(p => !p.fitbit_registration_requested && !p.fitbit_connected)
        }
      }
      
      return result
    })
    
    const totalParticipants = computed(() => participantStore.participants.length)
    
    const connectedCount = computed(() => 
      participantStore.participants.filter(p => p.fitbit_connected).length
    )
    
    const pendingCount = computed(() => 
      participantStore.participants.filter(p => p.fitbit_registration_requested && !p.fitbit_connected).length
    )
    
    return {
      loading: computed(() => fitbitStore.loading || participantStore.loading),
      error: computed(() => fitbitStore.error || participantStore.error),
      participants: computed(() => participantStore.participants),
      filteredParticipants,
      totalParticipants,
      connectedCount,
      pendingCount,
      search,
      statusFilter,
      showLinkModal,
      registrationLink,
      linkCopied,
      lastSyncDate,
      fetchingData,
      requesting,
      refreshFitbitData,
      fetchParticipantData,
      triggerDataFetch,
      syncParticipantData,
      exportData,
      requestRegistration,
      getRegistrationLink,
      copyLink,
      formatDate,
      getFitbitStatus,
      getFitbitStatusClass
    }
  }
})
</script>

<style scoped>
.progress {
  height: 8px;
  background-color: var(--gray-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--success-color);
}

.registration-link {
  background-color: var(--light-color);
  padding: 0.75rem;
  border-radius: var(--border-radius);
  font-family: monospace;
  overflow-x: auto;
  white-space: nowrap;
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

.table-responsive {
  overflow-x: auto;
}
</style>
