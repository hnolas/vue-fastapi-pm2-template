import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../plugins/axios'
import { Participant, ParticipantQueryParams } from '../types/participant'

export const useParticipantStore = defineStore('participants', () => {
  const participants = ref<Participant[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Fetch all participants
  const fetchParticipants = async (params: ParticipantQueryParams = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/participants/', {
        params
      })
      
      participants.value = response.data
      return response.data
    } catch (err: any) {
      console.error('Error fetching participants:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch participants'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Get a single participant by ID
  const getParticipant = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get(`/participants/${id}`)
      
      return response.data
    } catch (err: any) {
      console.error(`Error fetching participant ${id}:`, err)
      error.value = err.response?.data?.detail || 'Failed to fetch participant'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Create a new participant
  const createParticipant = async (participantData: Partial<Participant>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/participants/', participantData)
      
      // Add the new participant to the list
      participants.value.push(response.data)
      
      return response.data
    } catch (err: any) {
      console.error('Error creating participant:', err)
      error.value = err.response?.data?.detail || 'Failed to create participant'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Update an existing participant
  const updateParticipant = async (id: number, participantData: Partial<Participant>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.put(`/participants/${id}`, participantData)
      
      // Update the participant in the list
      const index = participants.value.findIndex(p => p.id === id)
      if (index !== -1) {
        participants.value[index] = response.data
      }
      
      return response.data
    } catch (err: any) {
      console.error(`Error updating participant ${id}:`, err)
      error.value = err.response?.data?.detail || 'Failed to update participant'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Delete a participant
  const deleteParticipant = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.delete(`/participants/${id}`)
      
      // Remove the participant from the list
      participants.value = participants.value.filter(p => p.id !== id)
      
      return true
    } catch (err: any) {
      console.error(`Error deleting participant ${id}:`, err)
      error.value = err.response?.data?.detail || 'Failed to delete participant'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Request Fitbit registration for a participant
  const requestFitbitRegistration = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post(`/fitbit/registration-request/${id}`, {})
      
      // Update the participant in the list
      const index = participants.value.findIndex(p => p.id === id)
      if (index !== -1) {
        participants.value[index].fitbit_registration_requested = true
      }
      
      return response.data
    } catch (err: any) {
      console.error(`Error requesting Fitbit registration for participant ${id}:`, err)
      error.value = err.response?.data?.detail || 'Failed to request Fitbit registration'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    participants,
    loading,
    error,
    fetchParticipants,
    getParticipant,
    createParticipant,
    updateParticipant,
    deleteParticipant,
    requestFitbitRegistration
  }
})
