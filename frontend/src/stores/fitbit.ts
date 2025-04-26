import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../plugins/axios'
import { FitbitToken, FitbitAuthRequest } from '../types/fitbit'

export const useFitbitStore = defineStore('fitbit', () => {
  const tokens = ref<FitbitToken[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Fetch all Fitbit tokens
  const fetchTokens = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/fitbit/tokens')
      
      tokens.value = response.data
      return response.data
    } catch (err: any) {
      console.error('Error fetching Fitbit tokens:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch Fitbit tokens'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Request Fitbit registration for a participant
  const requestRegistration = async (participantId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post(`/fitbit/registration-request/${participantId}`, {})
      
      return response.data
    } catch (err: any) {
      console.error(`Error requesting Fitbit registration for participant ${participantId}:`, err)
      error.value = err.response?.data?.detail || 'Failed to request Fitbit registration'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Trigger Fitbit data fetch for one or all participants
  const triggerDataFetch = async (participantId?: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post(
        '/fitbit/fetch-data', 
        {},
        {
          params: participantId ? { participant_id: participantId } : {}
        }
      )
      
      return response.data
    } catch (err: any) {
      console.error('Error triggering Fitbit data fetch:', err)
      error.value = err.response?.data?.detail || 'Failed to trigger Fitbit data fetch'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Create manual Fitbit authorization
  const createManualAuth = async (authData: FitbitAuthRequest) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/fitbit/auth', authData)
      
      return response.data
    } catch (err: any) {
      console.error('Error creating manual Fitbit auth:', err)
      error.value = err.response?.data?.detail || 'Failed to create Fitbit authorization'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Export data to Dropbox
  const exportData = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/fitbit/export-to-dropbox', {})
      return response.data
    } catch (err: any) {
      console.error('Error exporting Fitbit data to Dropbox:', err)
      error.value = err.response?.data?.detail || 'Failed to export data to Dropbox'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    tokens,
    loading,
    error,
    fetchTokens,
    requestRegistration,
    triggerDataFetch,
    createManualAuth,
    exportData
  }
})
