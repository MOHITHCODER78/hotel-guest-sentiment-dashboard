import datetime
import logging

from app import models
from app.database import SessionLocal
from app.ml_engine import ml_engine

logger = logging.getLogger(__name__)


def process_bulk_reviews(
    job_id: str,
    user_id: int,
    reviews: list[str],
    hotel_names: list[str | None] | None = None,
) -> None:
    """Process reviews in the background and persist results to PostgreSQL."""
    db = SessionLocal()
    job = db.query(models.ProcessingJob).filter(models.ProcessingJob.id == job_id).first()

    if not job:
        logger.error("Processing job %s not found", job_id)
        db.close()
        return

    try:
        job.status = "PROCESSING"
        db.commit()

        total = len(reviews)
        for index, review_text in enumerate(reviews):
            sentiments = ml_engine.analyze(review_text)
            hotel_name = None
            if hotel_names and index < len(hotel_names):
                hotel_name = hotel_names[index]

            new_review = models.ReviewRecord(
                text=review_text,
                user_id=user_id,
                hotel_name=hotel_name,
            )
            db.add(new_review)
            db.flush()

            for sentiment in sentiments:
                db.add(
                    models.AspectSentiment(
                        review_id=new_review.id,
                        aspect=sentiment.aspect,
                        sentiment=sentiment.sentiment,
                        score=sentiment.score,
                    )
                )

            if (index + 1) % 10 == 0 or index + 1 == total:
                job.processed_reviews = index + 1
                db.commit()

        job.status = "COMPLETED"
        job.processed_reviews = total
        job.completed_at = datetime.datetime.utcnow()
        db.commit()
        logger.info("Completed bulk job %s (%s reviews)", job_id, total)

    except Exception as exc:
        db.rollback()
        job = db.query(models.ProcessingJob).filter(models.ProcessingJob.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = str(exc)
            job.completed_at = datetime.datetime.utcnow()
            db.commit()
        logger.exception("Bulk job %s failed", job_id)

    finally:
        db.close()
