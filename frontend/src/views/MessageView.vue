<template>
  <div class="message-view">
    <div class="page-header mb-4">
      <h1 class="page-title">Messages</h1>
      <div class="view-tabs">
        <button 
          @click="activeTab = 'history'" 
          class="tab-button" 
          :class="{ 'active': activeTab === 'history' }"
        >
          History
        </button>
        <button 
          @click="activeTab = 'content'" 
          class="tab-button" 
          :class="{ 'active': activeTab === 'content' }"
        >
          Content Management
        </button>
        <button 
          @click="activeTab = 'stats'" 
          class="tab-button" 
          :class="{ 'active': activeTab === 'stats' }"
        >
          Statistics
        </button>
      </div>
    </div>

    <!-- Message History Tab -->
    <div v-if="activeTab === 'history'" class="card">
      <MessageHistory />
    </div>

    <!-- Message Content Management Tab -->
    <div v-if="activeTab === 'content'" class="card">
      <MessageContentManager />
    </div>

    <!-- Message Statistics Tab -->
    <div v-if="activeTab === 'stats'" class="card">
      <div class="card-header mb-3">
        <h2 class="card-title">Message Statistics</h2>
        <button @click="refreshStats" class="btn btn-outline btn-sm">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 4v6h6"></path><path d="M23 20v-6h-6"></path>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
          </svg>
          <span class="ml-1">Refresh</span>
        </button>
      </div>

      <!-- Loading state -->
      <div v-if="statsLoading" class="text-center p-4">
        <div class="spinner"></div>
        <p class="mt-2">Loading message statistics...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="statsError" class="alert alert-danger">
        {{ statsError }}
      </div>

      <!-- Stats content -->
      <div v-else class="stats-content">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="stat-box">
            <div class="stat-title">Total Messages</div>
            <div class="stat-value">{{ stats.total_messages || 0 }}</div>
          </div>
          
          <div class="stat-box">
            <div class="stat-title">Delivered</div>
            <div class="stat-value">{{ stats.delivered || 0 }}</div>
            <div class="stat-percent">
              {{ calculatePercent(stats.delivered, stats.total_messages) }}%
            </div>
          </div>
          
          <div class="stat-box">
            <div class="stat-title">Failed/Undelivered</div>
            <div class="stat-value">{{ (stats.failed || 0) + (stats.undelivered || 0) }}</div>
            <div class="stat-percent">
              {{ calculatePercent((stats.failed || 0) + (stats.undelivered || 0), stats.total_messages) }}%
            </div>
          </div>
          
          <div class="stat-box">
            <div class="stat-title">Participants Receiving</div>
            <div class="stat-value">{{ stats.distinct_participants || 0 }}</div>
          </div>
        </div>

        <div class="mt-4">
          <h3 class="text-lg font-medium mb-2">Message Status Distribution</h3>
          <div class="status-chart">
            <div 
              v-for="(count, status) in filteredStats" 
              :key="status" 
              class="chart-bar" 
              :style="{ width: `${calculatePercent(count, stats.total_messages)}%` }" 
              :class="getBarClass(status)"
            >
              <div class="chart-label">{{ status }}: {{ count }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import MessageHistory from '../components/MessageHistory.vue'
import MessageContentManager from '../components/MessageContentManager.vue'
import { useMessagesStore } from '../stores/messages'
import { useRoute, useRouter } from 'vue-router'

export default defineComponent({
  name: 'MessageView',
  
  components: {
    MessageHistory,
    MessageContentManager
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const messagesStore = useMessagesStore()
    
    // Tab management
    const activeTab = ref('history')
    
    // Check if there's a tab query parameter
    onMounted(() => {
      const tabParam = route.query.tab as string
      if (tabParam && ['history', 'content', 'stats'].includes(tabParam)) {
        activeTab.value = tabParam
      }
    })
    
    // Update URL when tab changes
    watch(activeTab, (newTab) => {
      router.replace({ query: { ...route.query, tab: newTab } })
    })
    
    // Stats data
    const stats = ref<any>({})
    const statsLoading = ref(false)
    const statsError = ref('')
    
    // Load message stats when stats tab is active
    watch(activeTab, (newTab) => {
      if (newTab === 'stats') {
        refreshStats()
      }
    })
    
    const refreshStats = async () => {
      statsLoading.value = true
      statsError.value = ''
      
      try {
        const statsData = await messagesStore.fetchMessageStats()
        stats.value = statsData
      } catch (err: any) {
        statsError.value = err.message || 'Failed to load message statistics'
      } finally {
        statsLoading.value = false
      }
    }
    
    const calculatePercent = (value: number, total: number) => {
      if (!total) return 0
      return Math.round((value / total) * 100)
    }
    
    const getBarClass = (status: string) => {
      switch (status) {
        case 'delivered':
          return 'bar-success'
        case 'sent':
          return 'bar-primary'
        case 'queued':
          return 'bar-secondary'
        case 'failed':
          return 'bar-danger'
        case 'undelivered':
          return 'bar-warning'
        default:
          return 'bar-secondary'
      }
    }
    
    // Filter out unwanted properties from stats for the chart
    const filteredStats = computed(() => {
      const result: Record<string, number> = {}
      
      // Only include actual message statuses
      const relevantKeys = ['delivered', 'sent', 'queued', 'failed', 'undelivered']
      
      for (const key of relevantKeys) {
        if (stats.value[key]) {
          result[key] = stats.value[key]
        }
      }
      
      return result
    })
    
    return {
      activeTab,
      stats,
      statsLoading,
      statsError,
      filteredStats,
      refreshStats,
      calculatePercent,
      getBarClass
    }
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-color);
}

.view-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.tab-button {
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-color);
  transition: all 0.2s;
}

.tab-button:hover {
  color: var(--primary-color);
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.stats-content {
  padding: 0 1rem 1rem;
}

.stat-box {
  padding: 1rem;
  background-color: var(--light-color);
  border-radius: var(--border-radius);
}

.stat-title {
  font-size: 0.875rem;
  color: var(--text-light);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
}

.stat-percent {
  font-size: 0.875rem;
  color: var(--text-light);
  margin-top: 0.25rem;
}

.status-chart {
  background-color: var(--light-color);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.chart-bar {
  height: 2.5rem;
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
  color: white;
  font-size: 0.875rem;
  min-width: 3rem;
}

.chart-label {
  white-space: nowrap;
}

.bar-success {
  background-color: var(--success-color);
}

.bar-primary {
  background-color: var(--primary-color);
}

.bar-secondary {
  background-color: var(--secondary-color);
}

.bar-danger {
  background-color: var(--danger-color);
}

.bar-warning {
  background-color: var(--warning-color);
  color: var(--dark-color);
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

@media (max-width: 768px) {
  .view-tabs {
    overflow-x: auto;
    width: 100%;
  }
  
  .tab-button {
    white-space: nowrap;
  }
}
</style>
