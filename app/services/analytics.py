from collections import defaultdict
import csv
from datetime import datetime
from io import StringIO

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.schemas import (
    AspectStat,
    CriticalIssue,
    InsightsResponse,
    KeywordsResponse,
    RecommendationItem,
    StatsResponse,
    TrendPoint,
    TrendsResponse,
)
from app.services.keyword_service import build_keywords

CRITICAL_THRESHOLD = 0.5

ASPECT_RECOMMENDATIONS = {
    "Staff": "Schedule service training and empower front-desk staff to resolve issues on first contact.",
    "Cleanliness": "Increase housekeeping inspections and publish daily room-quality checklists.",
    "Food": "Review breakfast timing, menu variety, and kitchen quality-control processes.",
    "Location": "Update website directions and highlight nearby transport options for guests.",
    "Value": "Review pricing against competitors and communicate included amenities more clearly.",
    "WiFi": "Upgrade network capacity and add a simple connectivity troubleshooting guide in rooms.",
    "General Experience": "Audit the end-to-end guest journey from check-in to checkout.",
}


def build_stats(db: Session, user_id: int, hotel: str | None = None) -> StatsResponse:
    review_query = db.query(models.ReviewRecord).filter(models.ReviewRecord.user_id == user_id)
    if hotel:
        review_query = review_query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))

    total_reviews = review_query.count()

    aspect_query = (
        db.query(
            models.AspectSentiment.aspect,
            func.count(models.AspectSentiment.id).label("count"),
            func.avg(models.AspectSentiment.score).label("avg_score"),
        )
        .join(models.ReviewRecord, models.ReviewRecord.id == models.AspectSentiment.review_id)
        .filter(models.ReviewRecord.user_id == user_id)
    )

    if hotel:
        aspect_query = aspect_query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))

    aspect_stats = aspect_query.group_by(models.AspectSentiment.aspect).all()
    breakdown = [
        AspectStat(
            aspect=row.aspect,
            count=row.count,
            avg_score=round(float(row.avg_score), 4),
        )
        for row in aspect_stats
    ]

    issues: list[CriticalIssue] = []
    for row in aspect_stats:
        avg_score = float(row.avg_score)
        if avg_score < CRITICAL_THRESHOLD:
            impact = "High" if avg_score < 0.3 else "Medium"
            issues.append(
                CriticalIssue(
                    issue=f"Poor {row.aspect} quality/service",
                    impact=impact,
                    frequency=f"{(avg_score * 100):.1f}% sentiment score",
                )
            )

    if not issues:
        issues = [
            CriticalIssue(
                issue="Platform Healthy",
                impact="None",
                frequency="100% stable",
            )
        ]

    return StatsResponse(
        total_reviews=total_reviews,
        aspect_breakdown=breakdown,
        critical_issues=issues,
    )


def build_trends(db: Session, user_id: int, period: str = "weekly", hotel: str | None = None) -> TrendsResponse:
    review_query = db.query(models.ReviewRecord).filter(models.ReviewRecord.user_id == user_id)
    if hotel:
        review_query = review_query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))

    reviews = review_query.order_by(models.ReviewRecord.created_at.asc()).all()
    buckets: dict[str, list[float]] = defaultdict(list)

    for review in reviews:
        sentiments = db.query(models.AspectSentiment).filter(models.AspectSentiment.review_id == review.id).all()
        if not sentiments:
            continue

        created = review.created_at or datetime.utcnow()
        label = created.strftime("%Y-%m") if period == "monthly" else created.strftime("%Y-W%W")
        avg_score = sum(item.score for item in sentiments) / len(sentiments)
        buckets[label].append(avg_score)

    points = [
        TrendPoint(
            period=label,
            avg_sentiment=round(sum(scores) / len(scores), 4),
            review_count=len(scores),
        )
        for label, scores in sorted(buckets.items())
    ]

    return TrendsResponse(period=period, points=points)


def build_insights(stats: StatsResponse) -> InsightsResponse:
    if stats.total_reviews == 0:
        return InsightsResponse(
            summary="No review data is available yet. Upload guest reviews to generate operational insights.",
            top_strength=None,
            top_weakness=None,
            recommendations=[
                RecommendationItem(
                    priority="Medium",
                    title="Upload your first review batch",
                    detail="Import a CSV of guest reviews to unlock aspect analytics and trend monitoring.",
                )
            ],
        )

    breakdown = stats.aspect_breakdown
    strongest = max(breakdown, key=lambda item: item.avg_score)
    weakest = min(breakdown, key=lambda item: item.avg_score)
    overall = sum(item.avg_score for item in breakdown) / len(breakdown)

    summary = (
        f"Across {stats.total_reviews} reviews, overall guest sentiment is "
        f"{overall * 100:.1f}%. Guests respond most positively to {strongest.aspect} "
        f"({strongest.avg_score * 100:.1f}%) and least positively to {weakest.aspect} "
        f"({weakest.avg_score * 100:.1f}%)."
    )

    recommendations: list[RecommendationItem] = []
    for item in sorted(breakdown, key=lambda row: row.avg_score):
        if item.avg_score >= CRITICAL_THRESHOLD:
            continue

        priority = "High" if item.avg_score < 0.3 else "Medium"
        recommendations.append(
            RecommendationItem(
                priority=priority,
                title=f"Improve {item.aspect}",
                detail=ASPECT_RECOMMENDATIONS.get(
                    item.aspect,
                    f"Investigate recurring complaints related to {item.aspect}.",
                ),
            )
        )

    if not recommendations:
        recommendations.append(
            RecommendationItem(
                priority="Low",
                title="Maintain current service standards",
                detail="Sentiment is healthy across tracked aspects. Continue monitoring trends after new review uploads.",
            )
        )

    return InsightsResponse(
        summary=summary,
        top_strength=strongest.aspect,
        top_weakness=weakest.aspect,
        recommendations=recommendations[:5],
    )


def export_analytics_csv(
    stats: StatsResponse,
    trends: TrendsResponse,
    keywords: KeywordsResponse,
) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["section", "name", "value", "count"])
    writer.writerow(["summary", "total_reviews", stats.total_reviews, ""])

    for item in stats.aspect_breakdown:
        writer.writerow(["aspect_breakdown", item.aspect, item.avg_score, item.count])

    for point in trends.points:
        writer.writerow(["trends", point.period, point.avg_sentiment, point.review_count])

    for item in keywords.overall_keywords:
        writer.writerow(["overall_keyword", item.term, item.score, ""])

    for item in keywords.positive_keywords:
        writer.writerow(["positive_keyword", item.term, item.score, ""])

    for item in keywords.negative_keywords:
        writer.writerow(["negative_keyword", item.term, item.score, ""])

    return buffer.getvalue()
