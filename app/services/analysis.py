from app.ml_engine import ml_engine
from app.schemas import AnalysisResponse, SentimentResult


def analyze_review_text(text: str) -> AnalysisResponse:
    sentiments = ml_engine.analyze(text)
    return AnalysisResponse(
        review=text,
        sentiments=[SentimentResult(**sentiment.model_dump()) for sentiment in sentiments],
    )
