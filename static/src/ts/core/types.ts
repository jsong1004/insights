/**
 * TypeScript Type Definitions
 * AI Insights Frontend Application
 */

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
}

export interface UserProfile {
  user_id: string;
  email: string;
  display_name: string;
  created_at: string;
  last_login: string;
  plan: SubscriptionPlan;
  usage_stats: UsageStats;
}

export type SubscriptionPlan = 'free' | 'basic' | 'pro' | 'enterprise';

// ============================================================================
// Usage Statistics Types
// ============================================================================

export interface UsageStats {
  daily: DailyUsage;
  monthly: MonthlyUsage;
  total: TotalUsage;
  plan_limits: PlanLimits;
}

export interface DailyUsage {
  insights_generated: number;
  tokens_used: number;
  last_reset: string;
}

export interface MonthlyUsage {
  insights_generated: number;
  tokens_used: number;
  month: string;
  last_reset: string;
}

export interface TotalUsage {
  insights_generated: number;
  tokens_used: number;
}

export interface PlanLimits {
  monthly_insights: number | null; // null = unlimited
  monthly_tokens: number | null;
  features: string[];
}

// ============================================================================
// Insights Types
// ============================================================================

export interface InsightItem {
  title: string;
  content: string;
  sources: Source[];
  confidence: number;
  category?: string;
}

export interface Source {
  title: string;
  url: string;
  snippet: string;
  relevance?: number;
}

export interface GeneratedInsights {
  topic: string;
  instructions: string;
  insights: InsightItem[];
  summary: string;
  metadata: InsightsMetadata;
  created_at: string;
  user_id: string;
  author_name?: string;
  author_email?: string;
  is_shared: boolean;
  likes_count: number;
  liked_by: string[];

  // Admin features
  is_pinned?: boolean;
  pinned_by?: string;
  pinned_at?: string;

  // Enhanced metadata
  view_count?: number;
  featured?: boolean;
  category?: string;
  language?: string;

  // Quality metrics
  quality_score?: number;
  engagement_score?: number;
}

export interface InsightsMetadata {
  total_sources: number;
  avg_confidence: number;
  processing_time?: number;
  tokens_used?: number;
  model?: string;
}

// ============================================================================
// Community Types
// ============================================================================

export interface CommunityInsight {
  id: string;
  topic: string;
  summary: string;
  insights_count: number;
  author_name: string;
  author_email: string;
  created_at: string;
  likes_count: number;
  is_liked_by_user: boolean;
  is_pinned?: boolean;
}

export interface TrendingTopic {
  topic: string;
  count: number;
  latest_date: string;
}

export interface CommunityStats {
  total_insights: number;
  total_users: number;
  total_likes: number;
  total_authors: number;
  trending_topics: TrendingTopic[];
}

// ============================================================================
// Admin Types
// ============================================================================

export interface PinResponse {
  success: boolean;
  is_pinned: boolean;
  message: string;
}

export interface LikeResponse {
  success: boolean;
  liked: boolean;
  likes: number;
}

export interface ShareResponse {
  success: boolean;
  is_shared: boolean;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface APIError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// ============================================================================
// Form Types
// ============================================================================

export interface InsightFormData {
  topic: string;
  instructions: string;
  source_type?: 'news' | 'academic' | 'general' | 'all';
  time_range?: 'day' | 'week' | 'month' | 'year' | 'all';
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface FlashMessage {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface TableSortState {
  column: string;
  direction: 'asc' | 'desc';
}

// ============================================================================
// Chart Types
// ============================================================================

export interface ChartDataPoint {
  label: string;
  value: number;
  date?: string;
}

export interface UsageChartData {
  labels: string[];
  insights: number[];
  tokens: number[];
}
