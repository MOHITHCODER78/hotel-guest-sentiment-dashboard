from app.ml_engine import ABSAEngine, detect_aspects, normalize_sentiment, split_sentences
from app.ml_engine import HOTEL_ASPECT_KEYWORDS


def test_split_sentences_handles_multiple_sentences():
    text = "The staff was great. The room was dirty."
    sentences = split_sentences(text)
    assert len(sentences) == 2


def test_detect_aspects_finds_staff_and_cleanliness():
    aspects = detect_aspects(
        "The staff was helpful but the bathroom was dirty.",
        HOTEL_ASPECT_KEYWORDS,
    )
    assert "Staff" in aspects
    assert "Cleanliness" in aspects


def test_normalize_sentiment_uppercases_label():
    label, score = normalize_sentiment("positive", 0.8123)
    assert label == "POSITIVE"
    assert score == 0.8123


def test_analyze_returns_multiple_aspects(ml_engine_with_mock):
    review = (
        "The staff was incredibly helpful and the room was spotless. "
        "However, the breakfast was cold."
    )
    results = ml_engine_with_mock.analyze(review)

    aspects = {result.aspect for result in results}
    assert "Staff" in aspects
    assert "Cleanliness" in aspects
    assert "Food" in aspects


def test_analyze_deduplicates_aspect_per_review(ml_engine_with_mock):
    review = "The staff was great and the staff was friendly."
    results = ml_engine_with_mock.analyze(review)
    staff_results = [result for result in results if result.aspect == "Staff"]
    assert len(staff_results) == 1


def test_analyze_fallback_for_general_experience(ml_engine_with_mock):
    review = "I had a wonderful stay overall."
    results = ml_engine_with_mock.analyze(review)
    assert len(results) == 1
    assert results[0].aspect == "General Experience"


def test_analyze_empty_text_returns_neutral():
    engine = ABSAEngine(classifier=lambda text: [{"label": "POSITIVE", "score": 0.5}])
    results = engine.analyze("   ")
    assert results[0].sentiment == "NEUTRAL"
    assert results[0].score == 0.0
