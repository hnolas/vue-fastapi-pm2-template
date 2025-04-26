import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../plugins/axios'
import { MessageContent, MessageContentQueryParams, MessageContentCreate, MessageContentUpdate } from '../types/message'

export const useMessageContentStore = defineStore('messageContent', () => {
  const messageContents = ref<MessageContent[]>([])
  const uniqueBuckets = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Fetch all message contents with optional filtering
  const fetchMessageContents = async (params: MessageContentQueryParams = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/message-content/', {
        params
      })
      
      messageContents.value = response.data
      return response.data
    } catch (err: any) {
      console.error('Error fetching message contents:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch message contents'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Fetch a specific message content by ID
  const getMessageContent = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get(`/message-content/${id}`)
      
      return response.data
    } catch (err: any) {
      console.error(`Error fetching message content ${id}:`, err)
      error.value = err.response?.data?.detail || `Failed to fetch message content #${id}`
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Create a new message content
  const createMessageContent = async (data: MessageContentCreate) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/message-content/', data)
      
      // Add to the existing list
      messageContents.value = [...messageContents.value, response.data]
      
      return response.data
    } catch (err: any) {
      console.error('Error creating message content:', err)
      error.value = err.response?.data?.detail || 'Failed to create message content'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Update an existing message content
  const updateMessageContent = async (id: number, data: MessageContentUpdate) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.put(`/message-content/${id}`, data)
      
      // Update in the existing list
      const index = messageContents.value.findIndex(item => item.id === id)
      if (index !== -1) {
        messageContents.value[index] = response.data
      }
      
      return response.data
    } catch (err: any) {
      console.error(`Error updating message content ${id}:`, err)
      error.value = err.response?.data?.detail || `Failed to update message content #${id}`
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Delete a message content
  const deleteMessageContent = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.delete(`/message-content/${id}`)
      
      // Remove from the existing list
      messageContents.value = messageContents.value.filter(item => item.id !== id)
      
      return true
    } catch (err: any) {
      console.error(`Error deleting message content ${id}:`, err)
      error.value = err.response?.data?.detail || `Failed to delete message content #${id}`
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Fetch unique bucket names
  const fetchUniqueBuckets = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/message-content/buckets/unique')
      
      uniqueBuckets.value = response.data
      return response.data
    } catch (err: any) {
      console.error('Error fetching unique buckets:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch bucket names'
      return []
    } finally {
      loading.value = false
    }
  }
  
  return {
    messageContents,
    uniqueBuckets,
    loading,
    error,
    fetchMessageContents,
    getMessageContent,
    createMessageContent,
    updateMessageContent,
    deleteMessageContent,
    fetchUniqueBuckets
  }
})