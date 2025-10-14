export interface Prompt {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  isTemplate: boolean;
  variables?: string[];
  usageCount: number;
  rating?: number;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  color: string;
  promptCount: number;
}

export interface Template {
  id: string;
  name: string;
  content: string;
  variables: string[];
  description: string;
  category: string;
}

export interface PromptAnalytics {
  promptId: string;
  usageCount: number;
  averageRating: number;
  lastUsed: Date;
  successRate: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  defaultCategory: string;
  autoSave: boolean;
  exportFormat: 'json' | 'txt' | 'md';
}
