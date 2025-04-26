<template>
  <div class="message-content-manager">
    <div class="card-header mb-3">
      <h2 class="card-title">Message Content Management</h2>
      <button @click="showAddForm = !showAddForm" class="btn btn-primary">
        <span v-if="!showAddForm">Add New Content</span>
        <span v-else>Cancel</span>
      </button>
    </div>

    <!-- New Message Content Form -->
    <div v-if="showAddForm" class="card mb-4">
      <div class="card-header mb-3">
        <h3 class="card-title">{{ editingContentId ? 'Edit' : 'Add' }} Message Content</h3>
      </div>
      <form @submit.prevent="saveMessageContent" class="message-content-form">
        <div class="form-group">
          <label for="content" class="form-label">Message Content</label>
          <textarea 
            id="content" 
            v-model="newContent.content" 
            class="form-control"
            rows="4"
            required
            placeholder="Enter message content"
          ></textarea>
          <div class="form-text mt-1">
            <small>{{ newContent.content.length }} characters</small>
          </div>
        </div>
        
        <div class="form-group">
          <label for="bucket" class="form-label">Bucket (Category)</label>
          <div class="bucket-input-container">
            <input 
              id="bucket" 
              v-model="newContent.bucket" 
              class="form-control"
              list="bucket-options"
              required
              placeholder="Enter bucket name"
            />
            <datalist id="bucket-options">
              <option v-for="bucket in uniqueBuckets" :key="bucket" :value="bucket"></option>
            </datalist>
          </div>
          <div class="form-text mt-1">
            <small>Group related messages into buckets/categories</small>
          </div>
        </div>
        
        <div class="form-group">
          <div class="form-check">
            <input 
              id="active" 
              v-model="newContent.active" 
              type="checkbox"
              class="form-check-input"
            />
            <label for="active" class="form-check-label">Active</label>
          </div>
          <div class="form-text mt-1">
            <small>Only active messages will be sent to participants</small>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ editingContentId ? 'Update' : 'Create' }} Message
          </button>
          <button 
            type="button" 
            @click="resetForm" 
            class="btn btn-outline ml-2"
          >
            Reset
          </button>
        </div>
      </form>
    </div>

    <!-- Filters -->
    <div class="filters mb-4 grid grid-cols-1 md:grid-cols-2 gap-3">
      <div class="form-group">
        <label for="bucketFilter" class="form-label">Filter by Bucket</label>
        <select id="bucketFilter" v-model="filters.bucket" class="form-control">
          <option :value="null">All Buckets</option>
          <option v-for="bucket in uniqueBuckets" :key="bucket" :value="bucket">{{ bucket }}</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="statusFilter" class="form-label">Status</label>
        <select id="statusFilter" v-model="filters.active" class="form-control">
          <option :value="null">All</option>
          <option :value="true">Active</option>
          <option :value="false">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner"></div>
      <p class="mt-2">Loading message content...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger">
      <p>{{ error }}</p>
      <button @click="loadMessageContents" class="btn btn-outline mt-2">Try Again</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="!messageContents.length" class="text-center p-4">
      <p v-if="hasFilters">No message contents found with the current filters.</p>
      <p v-else>No message contents available. Add your first message content above.</p>
      <button v-if="hasFilters" @click="resetFilters" class="btn btn-outline mt-2">Reset Filters</button>
    </div>

    <!-- Message contents display -->
    <div v-else class="message-content-list">
      <div v-for="content in messageContents" :key="content.id" class="message-content-item">
        <div class="message-content-header">
          <div class="message-content-meta">
            <div class="badge-container">
              <span class="badge" :class="content.active ? 'badge-success' : 'badge-secondary'">
                {{ content.active ? 'Active' : 'Inactive' }}
              </span>
              <span class="badge badge-primary ml-2">{{ content.bucket }}</span>
            </div>
            <span class="message-time">Added: {{ formatDateTime(content.created_at) }}</span>
          </div>
          <div class="message-content-actions">
            <button @click="editMessageContent(content)" class="btn btn-sm btn-outline">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" 
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              <span class="ml-1">Edit</span>
            </button>
            <button @click="confirmDelete(content)" class="btn btn-sm btn-danger ml-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" 
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
              <span class="ml-1">Delete</span>
            </button>
          </div>
        </div>
        <div class="message-content-body">
          {{ content.content }}
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirm Deletion</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this message content?</p>
          <p class="text-danger"><strong>This action cannot be undone.</strong></p>
        </div>
        <div class="modal-footer">
          <button @click="deleteMessageContent" class="btn btn-danger">Delete</button>
          <button @click="showDeleteConfirm = false" class="btn btn-outline ml-2">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import { useMessageContentStore } from '../stores/messageContent'

export default defineComponent({
  name: 'MessageContentManager',

  setup() {
    const messageContentStore = useMessageContentStore()
    
    // State for message content list and form
    const showAddForm = ref(false)
    const editingContentId = ref<number | null>(null)
    const showDeleteConfirm = ref(false)
    const contentToDelete = ref<number | null>(null)
    
    // Form data
    const newContent = ref({
      content: '',
      bucket: '',
      active: true
    })
    
    // Filters
    const filters = ref({
      bucket: null as string | null,
      active: null as boolean | null
    })
    
    // Initialize data
    onMounted(async () => {
      await loadMessageContents()
      await messageContentStore.fetchUniqueBuckets()
    })
    
    // Load message contents with current filters
    const loadMessageContents = async () => {
      const params: any = {}
      
      if (filters.value.bucket) {
        params.bucket = filters.value.bucket
      }
      
      if (filters.value.active !== null) {
        params.active = filters.value.active
      }
      
      await messageContentStore.fetchMessageContents(params)
    }
    
    // Watch for filter changes
    watch(filters, () => {
      loadMessageContents()
    })
    
    // Reset filters
    const resetFilters = () => {
      filters.value = {
        bucket: null,
        active: null
      }
    }
    
    // Computed property to check if any filters are applied
    const hasFilters = computed(() => {
      return filters.value.bucket !== null || filters.value.active !== null
    })
    
    // Handle form submission
    const saveMessageContent = async () => {
      try {
        if (editingContentId.value) {
          // Update existing content
          await messageContentStore.updateMessageContent(editingContentId.value, newContent.value)
        } else {
          // Create new content
          await messageContentStore.createMessageContent(newContent.value)
        }
        
        // Reset form and refresh data
        resetForm()
        showAddForm.value = false
        await loadMessageContents()
      } catch (err) {
        console.error('Error saving message content:', err)
      }
    }
    
    // Reset the form to defaults
    const resetForm = () => {
      newContent.value = {
        content: '',
        bucket: '',
        active: true
      }
      editingContentId.value = null
    }
    
    // Load content into form for editing
    const editMessageContent = (content: any) => {
      newContent.value = {
        content: content.content,
        bucket: content.bucket,
        active: content.active
      }
      editingContentId.value = content.id
      showAddForm.value = true
      
      // Scroll to form
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }, 100)
    }
    
    // Show delete confirmation
    const confirmDelete = (content: any) => {
      contentToDelete.value = content.id
      showDeleteConfirm.value = true
    }
    
    // Delete message content
    const deleteMessageContent = async () => {
      if (contentToDelete.value) {
        try {
          await messageContentStore.deleteMessageContent(contentToDelete.value)
          showDeleteConfirm.value = false
          contentToDelete.value = null
        } catch (err) {
          console.error('Error deleting message content:', err)
        }
      }
    }
    
    // Format date/time for display
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
    
    return {
      // State
      messageContents: computed(() => messageContentStore.messageContents),
      uniqueBuckets: computed(() => messageContentStore.uniqueBuckets),
      loading: computed(() => messageContentStore.loading),
      error: computed(() => messageContentStore.error),
      showAddForm,
      editingContentId,
      showDeleteConfirm,
      newContent,
      filters,
      hasFilters,
      
      // Methods
      loadMessageContents,
      saveMessageContent,
      resetForm,
      resetFilters,
      editMessageContent,
      confirmDelete,
      deleteMessageContent,
      formatDateTime
    }
  }
})
</script>

<style scoped>
.message-content-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-content-item {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1rem;
  border-left: 4px solid var(--primary-color);
}

.message-content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.message-content-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.badge-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-light);
}

.message-content-body {
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--text-color);
  white-space: pre-line;
}

.message-content-form {
  padding: 0 1rem 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  margin-top: 1.5rem;
}

.bucket-input-container {
  position: relative;
}

/* Modal styles */
.modal-overlay {
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

.modal-container {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  width: 100%;
  max-width: 400px;
  padding: 1.5rem;
}

.modal-header {
  margin-bottom: 1rem;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark-color);
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
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
  .message-content-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .message-content-actions {
    display: flex;
    width: 100%;
  }
  
  .message-content-actions button {
    flex: 1;
  }
}
</style>