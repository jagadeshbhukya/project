export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  communicationStyle: 'formal' | 'casual' | 'technical';
  responseLength: 'short' | 'medium' | 'detailed';
  interests: string[];
  timezone: string;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  conversationId: string;
  metadata?: {
    tokens?: number;
    processingTime?: number;
    confidence?: number;
  };
}

export interface Conversation {
  id: string;
  title: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  context?: ConversationContext;
}

export interface ConversationContext {
  summary: string;
  entities: string[];
  topics: string[];
  userIntent: string;
  previousContext?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface APIError {
  detail: string;
  status_code: number;
}