from typing import Any, Generic, List, Optional, TypeVar
from datetime import datetime

from pydantic import BaseModel, Field

T = TypeVar("T")


class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)


class SentimentResult(BaseModel):
    aspect: str
    sentiment: str
    score: float


class AnalysisResponse(BaseModel):
    review: str
    sentiments: List[SentimentResult]


class BulkUploadRequest(BaseModel):
    reviews: List[str] = Field(..., min_length=1, max_length=1000)


class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    total_reviews: int = 0
    processed_reviews: int = 0
    error_message: Optional[str] = None


class ReviewFeedItem(BaseModel):
    hotel: Optional[str]
    text: str
    analysis: List[SentimentResult]


class ReviewListItem(BaseModel):
    id: int
    hotel: Optional[str]
    text: str
    created_at: Optional[datetime]
    avg_score: Optional[float] = None
    analysis: List[SentimentResult]


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedReviewsResponse(BaseModel):
    items: List[ReviewListItem]
    meta: PaginationMeta


class TrendPoint(BaseModel):
    period: str
    avg_sentiment: float
    review_count: int


class TrendsResponse(BaseModel):
    period: str
    points: List[TrendPoint]


class KeywordStat(BaseModel):
    term: str
    score: float


class KeywordsResponse(BaseModel):
    overall_keywords: List[KeywordStat]
    positive_keywords: List[KeywordStat]
    negative_keywords: List[KeywordStat]


class RecommendationItem(BaseModel):
    priority: str
    title: str
    detail: str


class InsightsResponse(BaseModel):
    summary: str
    top_strength: Optional[str]
    top_weakness: Optional[str]
    recommendations: List[RecommendationItem]


class AspectStat(BaseModel):
    aspect: str
    count: int
    avg_score: float


class CriticalIssue(BaseModel):
    issue: str
    impact: str
    frequency: str


class StatsResponse(BaseModel):
    total_reviews: int
    aspect_breakdown: List[AspectStat]
    critical_issues: List[CriticalIssue]


class HealthResponse(BaseModel):
    status: str
    project: str
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class APIResponse(BaseModel, Generic[T]):
    data: T
