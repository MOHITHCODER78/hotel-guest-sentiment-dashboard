import csv
import io
from typing import Optional

from app.core.exceptions import AppError

MAX_CSV_ROWS = 1000


def _pick_review_text(row: dict[str, str]) -> str:
    normalized = {key.strip().lower(): value for key, value in row.items()}

    if normalized.get("full_review"):
        return normalized["full_review"].strip()

    negative = normalized.get("negative_review", "").strip()
    positive = normalized.get("positive_review", "").strip()
    if negative or positive:
        negative = negative.replace("No Negative", "").strip()
        positive = positive.replace("No Positive", "").strip()
        return f"{negative} {positive}".strip()

    for key in ("review", "text", "comment", "feedback"):
        if normalized.get(key):
            return normalized[key].strip()

    for value in normalized.values():
        if value and value.strip():
            return value.strip()

    return ""


def _pick_hotel_name(row: dict[str, str]) -> Optional[str]:
    normalized = {key.strip().lower(): value for key, value in row.items()}
    hotel = normalized.get("hotel_name") or normalized.get("hotel")
    return hotel.strip() if hotel else None


def parse_reviews_csv(
    file_content: bytes,
    max_rows: int = MAX_CSV_ROWS,
) -> tuple[list[str], list[Optional[str]]]:
    if not file_content:
        raise AppError("CSV file is empty.", code="empty_csv")

    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise AppError("CSV file must be UTF-8 encoded.", code="invalid_csv_encoding")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise AppError("CSV file has no header row.", code="invalid_csv_format")

    reviews: list[str] = []
    hotel_names: list[Optional[str]] = []

    for row in reader:
        if len(reviews) >= max_rows:
            break

        review_text = _pick_review_text(row)
        if not review_text:
            continue

        reviews.append(review_text)
        hotel_names.append(_pick_hotel_name(row))

    if not reviews:
        raise AppError("No valid review rows found in CSV.", code="empty_reviews")

    return reviews, hotel_names
