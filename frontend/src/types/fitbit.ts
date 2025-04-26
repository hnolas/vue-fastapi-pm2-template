export interface FitbitToken {
  id: number;
  participant_id: number;
  access_token: string;
  refresh_token: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface FitbitData {
  id: number;
  token_id: number;
  data_type: string;
  date: string;
  data: Record<string, any>;
  exported: boolean;
  created_at: string;
  updated_at: string;
}

export interface FitbitAuthRequest {
  participant_id: number;
  access_token: string;
  refresh_token: string;
  expires_at: string;
}