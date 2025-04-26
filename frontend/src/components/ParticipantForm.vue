<template>
  <div class="participant-form">
    <form @submit.prevent="submitForm">
      <div class="grid grid-cols-2 gap-3">
        <div class="form-group">
          <label for="pid" class="form-label">Participant ID (PID)</label>
          <input 
            id="pid" 
            v-model="form.pid" 
            type="text" 
            class="form-control" 
            required
            :disabled="isEdit"
          >
        </div>
        <div class="form-group">
          <label for="friendly_name" class="form-label">Friendly Name</label>
          <input 
            id="friendly_name" 
            v-model="form.friendly_name" 
            type="text" 
            class="form-control"
            placeholder="For %F token substitution in messages"
          >
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="form-group">
          <label for="phone_number" class="form-label">Phone Number</label>
          <input 
            id="phone_number" 
            v-model="form.phone_number" 
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
            v-model="form.study_group" 
            type="text" 
            class="form-control" 
            required
          >
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="form-group">
          <label for="start_date" class="form-label">Start Date</label>
          <input 
            id="start_date" 
            v-model="form.start_date" 
            type="date" 
            class="form-control"
          >
        </div>
        <div class="form-group">
          <label for="timezone_offset" class="form-label">Timezone Offset (minutes from UTC)</label>
          <input 
            id="timezone_offset" 
            v-model.number="form.timezone_offset" 
            type="number" 
            class="form-control"
            placeholder="e.g. -300 for EST"
          >
          <small class="text-muted">
            EST: -300, CST: -360, MST: -420, PST: -480
          </small>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="form-group">
          <label for="sms_window_start" class="form-label">SMS Window Start</label>
          <input 
            id="sms_window_start" 
            v-model="form.sms_window_start" 
            type="time" 
            class="form-control"
          >
        </div>
        <div class="form-group">
          <label for="sms_window_end" class="form-label">SMS Window End</label>
          <input 
            id="sms_window_end" 
            v-model="form.sms_window_end" 
            type="time" 
            class="form-control"
          >
        </div>
      </div>

      <div class="form-group">
        <div class="form-check">
          <input 
            id="active" 
            v-model="form.active" 
            type="checkbox" 
            class="form-check-input"
          >
          <label for="active" class="form-check-label">Active</label>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
      </div>

      <div class="form-group mt-4 flex justify-end gap-2">
        <button type="button" @click="$emit('cancel')" class="btn btn-outline">Cancel</button>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading">Saving...</span>
          <span v-else>{{ isEdit ? 'Update' : 'Add' }} Participant</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, PropType, watch } from 'vue'

interface Participant {
  id?: number;
  pid: string;
  friendly_name?: string;
  phone_number: string;
  study_group: string;
  start_date?: string;
  sms_window_start?: string;
  sms_window_end?: string;
  timezone_offset?: number;
  active: boolean;
  fitbit_connected?: boolean;
  fitbit_registration_requested?: boolean;
}

export default defineComponent({
  name: 'ParticipantForm',
  
  props: {
    participant: {
      type: Object as PropType<Participant>,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    }
  },
  
  emits: ['submit', 'cancel'],
  
  setup(props, { emit }) {
    const form = ref({
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
    
    const isEdit = computed(() => !!props.participant)
    
    // Watch for changes in the participant prop to update the form
    watch(() => props.participant, (newParticipant) => {
      if (newParticipant) {
        form.value = {
          pid: newParticipant.pid,
          friendly_name: newParticipant.friendly_name || '',
          phone_number: newParticipant.phone_number,
          study_group: newParticipant.study_group,
          start_date: newParticipant.start_date || '',
          sms_window_start: newParticipant.sms_window_start || '',
          sms_window_end: newParticipant.sms_window_end || '',
          timezone_offset: newParticipant.timezone_offset || 0,
          active: newParticipant.active
        }
      } else {
        // Reset form when participant is null
        form.value = {
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
    }, { immediate: true })
    
    const submitForm = () => {
      emit('submit', form.value)
    }
    
    return {
      form,
      isEdit,
      submitForm
    }
  }
})
</script>

<style scoped>
.form-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-check-input {
  width: 1rem;
  height: 1rem;
}

.text-muted {
  color: var(--text-light);
  font-size: 0.75rem;
}
</style>
