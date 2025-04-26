<template>
  <div class="home-view">
    <div class="page-header mb-4">
      <h1 class="page-title">Dashboard</h1>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner"></div>
      <p class="mt-2">Loading dashboard data...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Dashboard content -->
    <div v-else class="dashboard-content">
      <!-- Summary cards -->
      <div class="summary-cards-container mb-4">
        <div class="card stat-card">
          <div class="stat-icon participant-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-title">Participants</div>
            <div class="stat-value">{{ dashboardStats.participantCount }}</div>
            <div class="stat-desc">
              <span class="badge badge-success">{{ activeParticipantsCount }} active</span>
            </div>
          </div>
        </div>
        
        <div class="card stat-card">
          <div class="stat-icon message-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-title">Messages Sent</div>
            <div class="stat-value">{{ messageStats.total_messages || 0 }}</div>
            <div class="stat-desc">
              <span class="badge badge-success">{{ messageStats.delivered || 0 }} delivered</span>
              <span class="badge badge-danger ml-2">{{ messageStats.failed || 0 }} failed</span>
            </div>
          </div>
        </div>
        
        <div class="card stat-card">
          <div class="stat-icon fitbit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 20V10"></path>
              <path d="M12 20V4"></path>
              <path d="M6 20v-6"></path>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-title">Fitbit Connected</div>
            <div class="stat-value">{{ dashboardStats.fitbitConnectedCount }}</div>
            <div class="stat-desc">
              <span class="badge badge-warning">{{ dashboardStats.fitbitPendingCount }} pending</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Dashboard Sections Layout - side by side -->
      <div class="dashboard-sections-container">
        <!-- Recent activity -->
        <div class="card recent-messages-card">
          <div class="card-header mb-3">
            <h2 class="card-title">Recent Messages</h2>
            <router-link to="/messages" class="btn btn-outline btn-sm">
              View All
            </router-link>
          </div>
          
          <div v-if="recentMessages.length === 0" class="text-center p-4">
            <p>No recent messages found.</p>
          </div>
          
          <div v-else class="recent-messages">
            <div v-for="message in recentMessages" :key="message.id" class="message-item">
              <div class="message-meta">
                <span class="badge" :class="getStatusBadgeClass(message.status)">{{ message.status }}</span>
                <span class="message-time">{{ formatDateTime(message.sent_datetime) }}</span>
              </div>
              <div class="message-participant">
                To: {{ getParticipantName(message.participant_id) }}
              </div>
              <div class="message-content">
                {{ truncateText(message.content, 100) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Quick actions -->
        <div class="card quick-actions-card">
          <div class="card-header mb-3">
            <h2 class="card-title">Quick Actions</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="action-card">
              <router-link to="/participants" class="action-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="8.5" cy="7" r="4"></circle>
                  <line x1="20" y1="8" x2="20" y2="14"></line>
                  <line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
                <span>Add Participant</span>
              </router-link>
            </div>
            
            <div class="action-card">
              <router-link to="/fitbit" class="action-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
                </svg>
                <span>Manage Fitbit</span>
              </router-link>
            </div>
            
            <div class="action-card">
              <router-link to="/messages" class="action-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17 8h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2v4l-4-4H9a2 2 0 0 1-2-2v-1"></path>
                  <path d="M7 6h2a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5l-3 3V6a2 2 0 0 1 2-2h3z"></path>
                </svg>
                <span>View Messages</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useParticipantStore } from '../stores/participants'
import { useMessagesStore } from '../stores/messages'

export default defineComponent({
  name: 'HomeView',
  
  setup() {
    const participantStore = useParticipantStore()
    const messagesStore = useMessagesStore()
    
    const recentMessages = ref<any[]>([])
    const messageStats = ref<any>({})
    
    const loading = computed(() => {
      return participantStore.loading || messagesStore.loading
    })
    
    const error = computed(() => {
      return participantStore.error || messagesStore.error
    })
    
    // Computed properties for dashboard stats
    const dashboardStats = computed(() => {
      return {
        participantCount: participantStore.participants.length,
        activeParticipantsCount: participantStore.participants.filter(p => p.active).length,
        fitbitConnectedCount: participantStore.participants.filter(p => p.fitbit_connected).length,
        fitbitPendingCount: participantStore.participants.filter(
          p => p.fitbit_registration_requested && !p.fitbit_connected
        ).length
      }
    })
    
    const activeParticipantsCount = computed(() => {
      return participantStore.participants.filter(p => p.active).length
    })
    
    // Load data on component mount
    onMounted(async () => {
      await loadDashboardData()
    })
    
    const loadDashboardData = async () => {
      // Fetch participants if not already loaded
      if (participantStore.participants.length === 0) {
        await participantStore.fetchParticipants()
      }
      
      // Fetch recent messages
      const messagesResponse = await messagesStore.fetchMessages({ limit: 5 })
      recentMessages.value = messagesResponse
      
      // Fetch message stats
      const statsResponse = await messagesStore.fetchMessageStats()
      messageStats.value = statsResponse
    }
    
    // Helper functions
    const formatDateTime = (dateTime: string) => {
      const date = new Date(dateTime)
      return new Intl.DateTimeFormat('en-US', {
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
    
    const truncateText = (text: string, maxLength: number) => {
      if (text.length <= maxLength) return text
      return text.slice(0, maxLength) + '...'
    }
    
    return {
      loading,
      error,
      recentMessages,
      messageStats,
      dashboardStats,
      activeParticipantsCount,
      formatDateTime,
      getParticipantName,
      getStatusBadgeClass,
      truncateText
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

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.25rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
}

.participant-icon {
  background-color: var(--primary-color);
}

.message-icon {
  background-color: var(--success-color);
}

.fitbit-icon {
  background-color: var(--secondary-color);
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 0.875rem;
  color: var(--text-light);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.25rem 0;
}

.stat-desc {
  font-size: 0.875rem;
}

.recent-messages {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message-item {
  padding: 0.75rem;
  border-radius: var(--border-radius);
  background-color: var(--light-color);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-light);
}

.message-participant {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.message-content {
  font-size: 0.875rem;
}

.action-card {
  background-color: var(--light-color);
  border-radius: var(--border-radius);
  transition: background-color 0.2s;
}

.action-card:hover {
  background-color: #e2e8f0;
}

.action-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-decoration: none;
  color: var(--text-color);
}

.action-link:hover {
  text-decoration: none;
}

.action-link svg {
  margin-bottom: 0.75rem;
  color: var(--primary-color);
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

/* Dashboard Sections Layout */
.dashboard-sections-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .dashboard-sections-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .recent-messages-card, 
  .quick-actions-card {
    flex: 1;
    min-width: 0; /* Prevent flex items from overflowing */
  }
}

/* Summary Cards Layout */
.summary-cards-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .summary-cards-container {
    flex-direction: row;
    align-items: stretch;
  }
  
  .summary-cards-container .card {
    flex: 1;
    min-width: 0; /* Prevent flex items from overflowing */
  }
}
</style>
