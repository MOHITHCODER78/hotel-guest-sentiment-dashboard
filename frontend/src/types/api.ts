export interface ApiResponse<T> {
  data: T
}

export interface ApiError {
  error: {
    code: string
    message: string
  }
}

export interface User {
  id: number
  email: string
  full_name: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface SentimentResult {
  aspect: string
  sentiment: string
  score: number
}

export interface AnalysisResponse {
  review: string
  sentiments: SentimentResult[]
}

export interface TaskStatus {
  task_id: string
  status: string
  progress: number
  total_reviews: number
  processed_reviews: number
  error_message?: string | null
}

export interface ReviewFeedItem {
  hotel: string | null
  text: string
  analysis: SentimentResult[]
}

export interface ReviewListItem {
  id: number
  hotel: string | null
  text: string
  created_at: string | null
  avg_score?: number | null
  analysis: SentimentResult[]
}

export interface PaginationMeta {
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export interface PaginatedReviewsResponse {
  items: ReviewListItem[]
  meta: PaginationMeta
}

export interface AspectStat {
  aspect: string
  count: number
  avg_score: number
}

export interface CriticalIssue {
  issue: string
  impact: string
  frequency: string
}

export interface StatsResponse {
  total_reviews: number
  aspect_breakdown: AspectStat[]
  critical_issues: CriticalIssue[]
}

export interface TrendPoint {
  period: string
  avg_sentiment: number
  review_count: number
}

export interface TrendsResponse {
  period: string
  points: TrendPoint[]
}

export interface KeywordStat {
  term: string
  score: number
}

export interface KeywordsResponse {
  overall_keywords: KeywordStat[]
  positive_keywords: KeywordStat[]
  negative_keywords: KeywordStat[]
}

export interface RecommendationItem {
  priority: string
  title: string
  detail: string
}

export interface InsightsResponse {
  summary: string
  top_strength: string | null
  top_weakness: string | null
  recommendations: RecommendationItem[]
}

export interface ReviewFilters {
  page?: number
  page_size?: number
  search?: string
  aspect?: string
  sentiment?: string
  hotel?: string
  sort_by?: "created_at" | "hotel" | "sentiment_score"
  sort_order?: "asc" | "desc"
}
