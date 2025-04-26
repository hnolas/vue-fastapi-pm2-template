<template>
  <div class="message-history">
    <div class="card-header mb-3">
      <h2 class="card-title">Message History</h2>
      <div class="flex gap-2">
        <button @click="refreshMessages" class="btn btn-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 4v6h6"></path><path d="M23 20v-6h-6"></path>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
          </svg>
          <span class="ml-1">Refresh</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-4 grid grid-cols-3 gap-3">
      <div class="form-group">
        <label for="participantFilter" class="form-label">Participant</label>
        <select id="participantFilter" v-model="filters.participantId" class="form-control">
          <option :value="null">All Participants</option>
          <option v-for="participant in participants" :key="participant.id" :value="participant.id">
            {{ participant.pid }} ({{ participant.friendly_name || 'No name' }})
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="statusFilter" class="form-label">Status</label>
        <select id="statusFilter" v-model="filters.status" class="form-control">
          <option :value="null">All</option>
          <option value="sent">Sent</option>
          <option value="delivered">Delivered</option>
          <option value="failed">Failed</option>
          <option value="queued">Queued</option>
          <option value="undelivered">Undelivered</option>
        </select>
      </div>
      <div class="form-group">
        <label for="dateFilter" class="form-label">Date Range</label>
        <input 
          id="dateFilter" 
          v-model="filters.date" 
          type="date" 
          class="form-control" 
          placeholder="Filter by date"
        >
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner"></div>
      <p class="mt-2">Loading message history...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      <p>{{ error }}</p>
      <button @click="refreshMessages" class="btn btn-outline mt-2">Try Again</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="!messages.length" class="text-center p-4">
      <p>No messages found with the current filters.</p>
      <button @click="resetFilters" class="btn btn-outline mt-2">Reset Filters</button>
    </div>

    <!-- Messages display -->
    <div v-else class="message-list">
      <div v-for="message in messages" :key="message.id" class="message-item" :class="getMessageClass(message)">
        <div class="message-header">
          <div class="flex gap-2 items-center">
            <span class="badge" :class="getStatusBadgeClass(message.status)">{{ message.status }}</span>
            <span class="message-time">{{ formatDateTime(message.sent_datetime) }}</span>
          </div>
          <div v-if="message.status === 'failed' || message.status === 'undelivered'" class="message-actions">
            <button @click="resendMessage(message.id)" class="btn btn-sm btn-outline">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" 
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"></path>
              </svg>
              <span class="ml-1">Resend</span>
            </button>
          </div>
        </div>
        <div class="message-participant">
          To: {{ getParticipantName(message.participant_id) }} ({{ message.bucket }})
        </div>
        <div class="message-content">
          {{ message.content }}
        </div>
        <div v-if="message.error" class="message-error">
          Error: {{ message.error }}
        </div>
      </div>
    </div>

    <!-- Pagination controls if needed -->
    <div v-if="messages.length && totalPages > 1" class="pagination mt-4">
      <button 
        @click="changePage(currentPage - 1)" 
        class="btn btn-sm btn-outline" 
        :disabled="currentPage === 1"
      >
        Previous
      </button>
      <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button 
        @click="changePage(currentPage + 1)" 
        class="btn btn-sm btn-outline" 
        :disabled="currentPage === totalPages"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import { useMessagesStore } from '../stores/messages'
import { useParticipantStore } from '../stores/participants'

export default defineComponent({
  name: 'MessageHistory',
  
  setup() {
    const messagesStore = useMessagesStore()
    const participantStore = useParticipantStore()
    
    const filters = ref({
      participantId: null as number | null,
      status: null as string | null,
      date: null as string | null,
    })
    
    const currentPage = ref(1)
    const itemsPerPage = 20
    
    onMounted(async () => {
      if (participantStore.participants.length === 0) {
        await participantStore.fetchParticipants()
      }
      refreshMessages()
    })
    
    const refreshMessages = async () => {
      const params = {
        skip: (currentPage.value - 1) * itemsPerPage,
        limit: itemsPerPage,
        participant_id: filters.value.participantId,
        status: filters.value.status,
        start_date: filters.value.date,
      }
      
      await messagesStore.fetchMessages(params)
    }
    
    // Watch for filter changes and reset to page 1
    watch(filters, () => {
      currentPage.value = 1
      refreshMessages()
    })
    
    const resetFilters = () => {
      filters.value = {
        participantId: null,
        status: null,
        date: null,
      }
    }
    
    const totalPages = computed(() => {
      return Math.ceil(messagesStore.totalCount / itemsPerPage) || 1
    })
    
    const changePage = (page: number) => {
      currentPage.value = page
      refreshMessages()
    }
    
    const formatDateTime = (dateTime: string) => {
      const date = new Date(dateTime)
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      }).format(date)
    }
    
    const getParticipantName = (participantId: number) => {
      const participant = participantStore.participants.find(p => p.id === participantId)
      if (participant) {
        return `${participant.pid}${participant.friendly_name ? ` (${participant.friendly_name})` : ''}`
      }
      return `Participant #${participantId}`
    }
    
    const getStatusBadgeClass = (status: string) => {
      switch (status) {
        case 'delivered':
          return 'badge-success'
        case 'sent':
          return 'badge-primary'
        case 'queued':
          return 'badge-secondary'
        case 'failed':
          return 'badge-danger'
        case 'undelivered':
          return 'badge-warning'
        default:
          return 'badge-secondary'
      }
    }
    
    const getMessageClass = (message: any) => {
      return {
        'message-error': message.status === 'failed' || message.status === 'undelivered',
        'message-success': message.status === 'delivered',
        'message-pending': message.status === 'sent' || message.status === 'queued'
      }
    }
    
    const resendMessage = async (messageId: number) => {
      await messagesStore.resendMessage(messageId)
      refreshMessages()
    }
    
    return {
      messages: computed(() => messagesStore.messages),
      loading: computed(() => messagesStore.loading),
      error: computed(() => messagesStore.error),
      participants: computed(() => participantStore.participants),
      filters,
      currentPage,
      totalPages,
      refreshMessages,
      resetFilters,
      changePage,
      formatDateTime,
      getParticipantName,
      getStatusBadgeClass,
      getMessageClass,
      resendMessage
    }
  }
})
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1rem;
  border-left: 4px solid var(--secondary-color);
}

.message-item.message-error {
  border-left-color: var(--danger-color);
}

.message-item.message-success {
  border-left-color: var(--success-color);
}

.message-item.message-pending {
  border-left-color: var(--primary-color);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-time {
  color: var(--text-light);
  font-size: 0.875rem;
}

.message-participant {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.message-content {
  margin-bottom: 0.5rem;
  word-break: break-word;
}

.message-error {
  color: var(--danger-color);
  font-size: 0.875rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-light);
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
</style>
