export interface User {
  _id: string;
  username: string;
  email: string;
  interests: string[];
  userType: string;
  token?: string;
}

export interface Therapist {
  _id: string;
  name: string;
  email: string;
  specializations: string[];
  userType: string;
  document?: {
    isVerified: boolean;
  };
  token?: string;
}

export interface AuthState {
  user: User | Therapist | null;
  isLoading: boolean;
  error: string | null;
}