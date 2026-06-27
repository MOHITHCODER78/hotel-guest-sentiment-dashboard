import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_current_user
from app.core.exceptions import AppError
from app.database import get_db
from app.schemas import APIResponse, BulkUploadRequest, TaskStatusResponse
from app.services.bulk_processor import process_bulk_reviews
from app.services.csv_parser import parse_reviews_csv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _build_job_response(job: models.ProcessingJob) -> TaskStatusResponse:
    progress = (
        job.processed_reviews / job.total_reviews
        if job.total_reviews > 0
        else 0.0
    )
    return TaskStatusResponse(
        task_id=job.id,
        status=job.status,
        progress=round(progress, 4),
        total_reviews=job.total_reviews,
        processed_reviews=job.processed_reviews,
        error_message=job.error_message,
    )


def _queue_bulk_job(
    background_tasks: BackgroundTasks,
    db: Session,
    current_user: models.User,
    reviews: list[str],
    hotel_names: list[str | None] | None = None,
) -> TaskStatusResponse:
    job_id = str(uuid.uuid4())
    job = models.ProcessingJob(
        id=job_id,
        user_id=current_user.id,
        status="PENDING",
        total_reviews=len(reviews),
        processed_reviews=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_bulk_reviews,
        job_id,
        current_user.id,
        reviews,
        hotel_names,
    )
    logger.info("Queued bulk job %s for user %s (%s reviews)", job_id, current_user.id, len(reviews))

    return _build_job_response(job)


@router.post("/bulk-upload", response_model=APIResponse[TaskStatusResponse])
async def bulk_upload(
    request: BulkUploadRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cleaned_reviews = [review.strip() for review in request.reviews if review.strip()]
    if not cleaned_reviews:
        raise AppError("At least one non-empty review is required.", code="empty_reviews")

    job_response = _queue_bulk_job(background_tasks, db, current_user, cleaned_reviews)
    return APIResponse(data=job_response)


@router.post("/csv-upload", response_model=APIResponse[TaskStatusResponse])
async def csv_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise AppError("Only CSV files are supported.", code="invalid_file_type")

    file_content = await file.read()
    reviews, hotel_names = parse_reviews_csv(file_content)

    job_response = _queue_bulk_job(
        background_tasks,
        db,
        current_user,
        reviews,
        hotel_names,
    )
    return APIResponse(data=job_response)


@router.get("/{task_id}", response_model=APIResponse[TaskStatusResponse])
async def get_job_status(
    task_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(models.ProcessingJob)
        .filter(
            models.ProcessingJob.id == task_id,
            models.ProcessingJob.user_id == current_user.id,
        )
        .first()
    )
    if not job:
        raise AppError("Job not found.", status_code=404, code="job_not_found")

    return APIResponse(data=_build_job_response(job))
