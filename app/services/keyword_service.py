from __future__ import annotations

from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import Session

from app import models
from app.schemas import KeywordStat, KeywordsResponse

STOP_WORDS = "english"


def _extract_keywords(texts: list[str], limit: int) -> list[KeywordStat]:
    cleaned = [text.strip() for text in texts if text and text.strip()]
    if not cleaned:
        return []

    if len(cleaned) == 1:
        words = [word.strip(".,!?;:\"'()[]{}") for word in cleaned[0].lower().split()]
        counts = Counter(word for word in words if len(word) > 2)
        return [KeywordStat(term=term, score=round(float(score), 4)) for term, score in counts.most_common(limit)]

    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, max_features=max(limit * 4, 20), ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(cleaned)
    scores = matrix.mean(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda item: item[1], reverse=True)
    return [KeywordStat(term=term, score=round(float(score), 4)) for term, score in ranked[:limit]]


def build_keywords(
    db: Session,
    user_id: int,
    hotel: str | None = None,
    aspect: str | None = None,
    sentiment: str | None = None,
    limit: int = 10,
) -> KeywordsResponse:
    query = (
        db.query(models.ReviewRecord.text, models.AspectSentiment.sentiment)
        .join(models.AspectSentiment, models.AspectSentiment.review_id == models.ReviewRecord.id)
        .filter(models.ReviewRecord.user_id == user_id)
    )

    if hotel:
        query = query.filter(models.ReviewRecord.hotel_name.ilike(f"%{hotel.strip()}%"))
    if aspect:
        query = query.filter(models.AspectSentiment.aspect.ilike(aspect.strip()))
    if sentiment:
        query = query.filter(models.AspectSentiment.sentiment.ilike(sentiment.strip()))

    rows = query.all()
    overall_texts = [row.text for row in rows]
    positive_texts = [row.text for row in rows if row.sentiment.upper() == "POSITIVE"]
    negative_texts = [row.text for row in rows if row.sentiment.upper() == "NEGATIVE"]

    return KeywordsResponse(
        overall_keywords=_extract_keywords(overall_texts, limit),
        positive_keywords=_extract_keywords(positive_texts, limit),
        negative_keywords=_extract_keywords(negative_texts, limit),
    )