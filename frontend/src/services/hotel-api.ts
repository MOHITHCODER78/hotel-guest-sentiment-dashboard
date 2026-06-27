import { apiRequest } from "@/lib/api"
import { getToken } from "@/lib/auth-storage"
import type {
  AnalysisResponse,
  InsightsResponse,
  KeywordsResponse,
  PaginatedReviewsResponse,
  ReviewFeedItem,
  ReviewFilters,
  StatsResponse,
  TaskStatus,
  TrendsResponse,
} from "@/types/api"

const API_BASE = import.meta.env.VITE_API_URL ?? ""

export function fetchStats(hotel?: string) {
  const params = new URLSearchParams()
  if (hotel) params.set("hotel", hotel)
  return apiRequest<StatsResponse>(`/api/v1/analytics/stats${params.toString() ? `?${params.toString()}` : ""}`)
}

export function fetchTrends(period: "weekly" | "monthly" = "weekly", hotel?: string) {
  const params = new URLSearchParams({ period })
  if (hotel) params.set("hotel", hotel)
  return apiRequest<TrendsResponse>(`/api/v1/analytics/trends?${params.toString()}`)
}

export function fetchInsights(hotel?: string) {
  const params = new URLSearchParams()
  if (hotel) params.set("hotel", hotel)
  return apiRequest<InsightsResponse>(`/api/v1/analytics/insights${params.toString() ? `?${params.toString()}` : ""}`)
}

export function fetchKeywords(hotel?: string) {
  const params = new URLSearchParams()
  if (hotel) params.set("hotel", hotel)
  return apiRequest<KeywordsResponse>(`/api/v1/analytics/keywords${params.toString() ? `?${params.toString()}` : ""}`)
}

export function fetchLatestReviews() {
  return apiRequest<ReviewFeedItem[]>("/api/v1/reviews/latest")
}

export function fetchReviews(filters: ReviewFilters = {}) {
  const params = new URLSearchParams()
  if (filters.page) params.set("page", String(filters.page))
  if (filters.page_size) params.set("page_size", String(filters.page_size))
  if (filters.search) params.set("search", filters.search)
  if (filters.aspect) params.set("aspect", filters.aspect)
  if (filters.sentiment) params.set("sentiment", filters.sentiment)
  if (filters.hotel) params.set("hotel", filters.hotel)
  if (filters.sort_by) params.set("sort_by", filters.sort_by)
  if (filters.sort_order) params.set("sort_order", filters.sort_order)

  const query = params.toString()
  return apiRequest<PaginatedReviewsResponse>(`/api/v1/reviews${query ? `?${query}` : ""}`)
}

export async function downloadReviewsCsv(filters: ReviewFilters = {}) {
  const token = getToken()
  const params = new URLSearchParams()
  if (filters.search) params.set("search", filters.search)
  if (filters.aspect) params.set("aspect", filters.aspect)
  if (filters.sentiment) params.set("sentiment", filters.sentiment)
  if (filters.hotel) params.set("hotel", filters.hotel)

  const response = await fetch(`${API_BASE}/api/v1/reviews/export.csv${params.toString() ? `?${params.toString()}` : ""}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!response.ok) throw new Error("Failed to download review export")

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = "hotel-reviews-export.csv"
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function downloadAnalyticsCsv(hotel?: string) {
  const token = getToken()
  const params = new URLSearchParams()
  if (hotel) params.set("hotel", hotel)

  const response = await fetch(`${API_BASE}/api/v1/analytics/export.csv${params.toString() ? `?${params.toString()}` : ""}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!response.ok) throw new Error("Failed to download analytics export")

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = "hotel-analytics-export.csv"
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export function analyzeReview(text: string) {
  return apiRequest<AnalysisResponse>("/api/v1/analyze", {
    method: "POST",
    body: JSON.stringify({ text }),
  })
}

export function uploadCsv(file: File) {
  const formData = new FormData()
  formData.append("file", file)

  return apiRequest<TaskStatus>("/api/v1/jobs/csv-upload", {
    method: "POST",
    body: formData,
  })
}

export function fetchJobStatus(taskId: string) {
  return apiRequest<TaskStatus>(`/api/v1/jobs/${taskId}`)
}

export async function downloadPdfReport() {
  const token = getToken()
  const response = await fetch(`${API_BASE}/api/v1/analytics/report/pdf`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!response.ok) {
    throw new Error("Failed to download report")
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = "hotel-sentiment-report.pdf"
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
