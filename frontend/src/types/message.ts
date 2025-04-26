export interface Message {
  id: number;
  participant_id: number;
  content_id?: number;
  content: string;
  bucket: string;
  status: string;
  sent_datetime: string;
  delivered_datetime?: string;
  twilio_sid?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface MessageContent {
  id: number;
  content: string;
  bucket: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MessageQueryParams {
  skip?: number;
  limit?: number;
  participant_id?: number;
  pid?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
}

export interface MessageContentQueryParams {
  skip?: number;
  limit?: number;
  bucket?: string;
  active?: boolean;
}

export interface MessageContentCreate {
  content: string;
  bucket: string;
  active?: boolean;
}

export interface MessageContentUpdate {
  content?: string;
  bucket?: string;
  active?: boolean;
}

export interface MessageStatsQueryParams {
  start_date?: string;
  end_date?: string;
}