export interface Participant {
  id: number;
  pid: string;
  friendly_name?: string;
  phone_number: string;
  study_group: string;
  start_date?: string;
  sms_window_start?: string;
  sms_window_end?: string;
  timezone_offset?: number;
  active: boolean;
  fitbit_connected: boolean;
  fitbit_registration_requested: boolean;
  created_at: string;
  updated_at: string;
}

export interface ParticipantQueryParams {
  skip?: number;
  limit?: number;
  active?: boolean;
  study_group?: string;
}