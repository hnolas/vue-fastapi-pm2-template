import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../plugins/axios'
import { Message, MessageQueryParams, MessageStatsQueryParams } from '../types/message'

export const useMessagesStore = defineStore('messages', () => {
  const messages = ref<Message[]>([])
  const totalCount = ref(0)
  const stats = ref<Record<string, number>>({})
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Fetch message history with optional filters
  const fetchMessages = async (params: MessageQueryParams = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/sms/history', {
        params
      })
      
      messages.value = response.data
      
      // Estimate total count based on response
      // In a real implementation, this would come from pagination metadata
      totalCount.value = response.data.length >= (params.limit || 100) ? 
        (params.skip || 0) + response.data.length + 1 : 
        (params.skip || 0) + response.data.length
      
      return response.data
    } catch (err: any) {
      console.error('Error fetching message history:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch message history'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Fetch message statistics
  const fetchMessageStats = async (params: MessageStatsQueryParams = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/sms/stats', {
        params
      })
      
      stats.value = response.data
      return response.data
    } catch (err: any) {
      console.error('Error fetching message stats:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch message statistics'
      return {}
    } finally {
      loading.value = false
    }
  }
  
  // Fetch SMS window times
  const fetchSmsWindowTimes = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/sms/window-times')
      
      return response.data
    } catch (err: any) {
      console.error('Error fetching SMS window times:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch SMS window times'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Resend a failed message
  const resendMessage = async (messageId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post(`/sms/resend/${messageId}`, {})
      
      // Update the message in the list
      const index = messages.value.findIndex(m => m.id === messageId)
      if (index !== -1) {
        messages.value[index] = response.data
      }
      
      return response.data
    } catch (err: any) {
      console.error(`Error resending message ${messageId}:`, err)
      error.value = err.response?.data?.detail || 'Failed to resend message'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    messages,
    totalCount,
    stats,
    loading,
    error,
    fetchMessages,
    fetchMessageStats,
    fetchSmsWindowTimes,
    resendMessage
  }
})
