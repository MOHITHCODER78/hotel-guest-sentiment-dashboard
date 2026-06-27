import nltk
from typing import Callable, List, Optional

from app.schemas import SentimentResult

HOTEL_ASPECT_KEYWORDS = {
    "Staff": ["staff", "service", "reception", "manager", "waiter", "concierge", "desk"],
    "Cleanliness": ["clean", "dirty", "spotless", "housekeeping", "dust", "bathroom", "tidy"],
    "Food": ["food", "breakfast", "dinner", "restaurant", "meal", "buffet", "lunch"],
    "Location": ["location", "place", "area", "beach", "city", "nearby", "central"],
    "Value": ["value", "price", "expensive", "cheap", "cost", "money", "worth"],
    "WiFi": ["wifi", "wi-fi", "internet", "connection", "signal", "bandwidth"],
}


def _ensure_nltk_punkt() -> None:
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)


def split_sentences(text: str) -> List[str]:
    _ensure_nltk_punkt()
    cleaned = text.strip()
    if not cleaned:
        return []
    return nltk.tokenize.sent_tokenize(cleaned)


def detect_aspects(sentence: str, aspect_keywords: dict[str, list[str]]) -> List[str]:
    sentence_lower = sentence.lower()
    return [
        aspect
        for aspect, keywords in aspect_keywords.items()
        if any(keyword in sentence_lower for keyword in keywords)
    ]


def normalize_sentiment(label: str, score: float) -> tuple[str, float]:
    normalized_label = label.strip().upper()
    if normalized_label not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
        normalized_label = "NEUTRAL"
    return normalized_label, round(float(score), 4)


class ABSAEngine:
    def __init__(self, classifier: Optional[Callable[[str], list[dict]]] = None):
        self._classifier = classifier
        self.aspect_keywords = HOTEL_ASPECT_KEYWORDS

    @property
    def classifier(self):
        if self._classifier is None:
            from transformers import pipeline

            self._classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
            )
        return self._classifier

    def _infer(self, text: str) -> tuple[str, float]:
        result = self.classifier(text)[0]
        return normalize_sentiment(result["label"], result["score"])

    def analyze(self, text: str) -> List[SentimentResult]:
        if not text or not text.strip():
            return [
                SentimentResult(
                    aspect="General Experience",
                    sentiment="NEUTRAL",
                    score=0.0,
                )
            ]

        aspect_results: dict[str, SentimentResult] = {}

        for sentence in split_sentences(text):
            aspects = detect_aspects(sentence, self.aspect_keywords)
            if not aspects:
                continue

            label, score = self._infer(sentence)
            for aspect in aspects:
                existing = aspect_results.get(aspect)
                if existing is None or score > existing.score:
                    aspect_results[aspect] = SentimentResult(
                        aspect=aspect,
                        sentiment=label,
                        score=score,
                    )

        if not aspect_results:
            label, score = self._infer(text)
            aspect_results["General Experience"] = SentimentResult(
                aspect="General Experience",
                sentiment=label,
                score=score,
            )

        return list(aspect_results.values())


ml_engine = ABSAEngine()
