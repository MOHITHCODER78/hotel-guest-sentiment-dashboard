import math
from io import StringIO
import csv

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app import models
from app.api.deps import get_current_user
from app.database import get_db
from app.schemas import (
    APIResponse,
    PaginatedReviewsResponse,
    PaginationMeta,
    ReviewFeedItem,
    ReviewListItem,
    SentimentResult,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _serialize_review(review: models.ReviewRecord, truncate: bool = False) -> ReviewListItem:
    text = review.text
    if truncate and len(text) > 200:
        text = text[:200] + "..."

    return ReviewListItem(
        id=review.id,
        hotel=review.hotel_name,
        text=text,
        created_at=review.created_at,
        avg_score=round(sum(item.score for item in review.sentiments) / len(review.sentiments), 4)
        if review.sentiments
        else None,
        analysis=[
            SentimentResult(aspect=item.aspect, sentiment=item.sentiment, score=item.score)
            for item in review.sentiments
        ],
    )


@router.get("", response_model=APIResponse[PaginatedReviewsResponse])
async def list_reviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    aspect: str | None = None,
    sentiment: str | None = None,
    hotel: str | None = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|hotel|sentiment_score)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.ReviewRecord)
        .options(joinedload(models.ReviewRecord.sentiments))
        .filter(models.ReviewRecord.user_id == current_user.id)
    )

    if search:
        query = query.filter(models.ReviewRecord.text.ilike(f"%{search.strip()}%"))

    if hotel:
        query = query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))

    if aspect or sentiment:
        query = query.join(models.AspectSentiment)
        if aspect:
            query = query.filter(models.AspectSentiment.aspect.ilike(aspect.strip()))
        if sentiment:
            query = query.filter(models.AspectSentiment.sentiment.ilike(sentiment.strip()))
        query = query.distinct()

    total_items = query.count()
    total_pages = max(1, math.ceil(total_items / page_size)) if total_items else 1

    if sort_by == "hotel":
        order_column = models.ReviewRecord.hotel_name.asc() if sort_order == "asc" else models.ReviewRecord.hotel_name.desc()
        query = query.order_by(order_column, models.ReviewRecord.id.desc())
    else:
        query = query.order_by(
            models.ReviewRecord.created_at.asc() if sort_order == "asc" else models.ReviewRecord.created_at.desc()
        )

    reviews = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    serialized_reviews = [_serialize_review(review) for review in reviews]
    if sort_by == "sentiment_score":
        serialized_reviews = sorted(
            serialized_reviews,
            key=lambda item: item.avg_score if item.avg_score is not None else -1,
            reverse=sort_order == "desc",
        )

    return APIResponse(
        data=PaginatedReviewsResponse(
            items=serialized_reviews,
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )
    )


@router.get("/export.csv")
async def export_reviews_csv(
    search: str | None = None,
    aspect: str | None = None,
    sentiment: str | None = None,
    hotel: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.ReviewRecord)
        .options(joinedload(models.ReviewRecord.sentiments))
        .filter(models.ReviewRecord.user_id == current_user.id)
    )

    if search:
        query = query.filter(models.ReviewRecord.text.ilike(f"%{search.strip()}%"))
    if hotel:
        query = query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))
    if aspect or sentiment:
        query = query.join(models.AspectSentiment)
        if aspect:
            query = query.filter(models.AspectSentiment.aspect.ilike(aspect.strip()))
        if sentiment:
            query = query.filter(models.AspectSentiment.sentiment.ilike(sentiment.strip()))
        query = query.distinct()

    reviews = query.order_by(models.ReviewRecord.created_at.desc()).all()

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["review_id", "hotel_name", "created_at", "review_text", "aspect", "sentiment", "score"])
    for review in reviews:
        for item in review.sentiments:
            writer.writerow([
                review.id,
                review.hotel_name or "",
                review.created_at.isoformat() if review.created_at else "",
                review.text,
                item.aspect,
                item.sentiment,
                item.score,
            ])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="hotel-reviews-export.csv"'},
    )


@router.get("/latest", response_model=APIResponse[list[ReviewFeedItem]])
async def get_latest_reviews(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(models.ReviewRecord)
        .options(joinedload(models.ReviewRecord.sentiments))
        .filter(models.ReviewRecord.user_id == current_user.id)
        .order_by(models.ReviewRecord.id.desc())
        .limit(10)
        .all()
    )

    feed = [
        ReviewFeedItem(
            hotel=review.hotel_name,
            text=review.text[:200] + "..." if len(review.text) > 200 else review.text,
            analysis=[
                SentimentResult(aspect=item.aspect, sentiment=item.sentiment, score=item.score)
                for item in review.sentiments
            ],
        )
        for review in reviews
    ]

    return APIResponse(data=feed)
