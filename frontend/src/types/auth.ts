export interface Token {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  username: string;
  email?: string;
  is_active: boolean;
  is_superuser: boolean;
}