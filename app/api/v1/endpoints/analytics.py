from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_current_user
from app.database import get_db
from app.schemas import APIResponse, InsightsResponse, KeywordsResponse, StatsResponse, TrendsResponse
from app.services.analytics import build_insights, build_stats, build_trends, export_analytics_csv
from app.services.keyword_service import build_keywords
from app.services.pdf_report import generate_pdf_report

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats", response_model=APIResponse[StatsResponse])
async def get_stats(
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(data=build_stats(db, current_user.id, hotel))


@router.get("/trends", response_model=APIResponse[TrendsResponse])
async def get_trends(
    period: str = Query(default="weekly", pattern="^(weekly|monthly)$"),
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(data=build_trends(db, current_user.id, period, hotel))


@router.get("/insights", response_model=APIResponse[InsightsResponse])
async def get_insights(
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = build_stats(db, current_user.id, hotel)
    return APIResponse(data=build_insights(stats))


@router.get("/keywords", response_model=APIResponse[KeywordsResponse])
async def get_keywords(
    hotel: str | None = None,
    aspect: str | None = None,
    sentiment: str | None = None,
    limit: int = Query(default=10, ge=1, le=25),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIResponse(
        data=build_keywords(db, current_user.id, hotel=hotel, aspect=aspect, sentiment=sentiment, limit=limit)
    )


@router.get("/export.csv")
async def export_analytics(
    period: str = Query(default="weekly", pattern="^(weekly|monthly)$"),
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = build_stats(db, current_user.id, hotel)
    trends = build_trends(db, current_user.id, period, hotel)
    keywords = build_keywords(db, current_user.id, hotel=hotel)
    content = export_analytics_csv(stats, trends, keywords)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="hotel-analytics-export.csv"'},
    )


@router.get("/report/pdf")
async def download_pdf_report(
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = build_stats(db, current_user.id, hotel)
    trends = build_trends(db, current_user.id, "weekly", hotel)
    insights = build_insights(stats)
    pdf_bytes = generate_pdf_report(
        stats,
        trends,
        insights,
        manager_name=current_user.full_name or current_user.email,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="hotel-sentiment-report.pdf"'},
    )
