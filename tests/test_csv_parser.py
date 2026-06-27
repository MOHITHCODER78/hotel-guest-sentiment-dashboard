import io

from app.services.csv_parser import parse_reviews_csv


def test_parse_kaggle_style_csv():
    csv_content = (
        "Hotel_Name,Negative_Review,Positive_Review\n"
        "London Inn,Dirty room,Slow wifi\n"
        "Paris Hotel,No Negative,Great staff\n"
    ).encode("utf-8")

    reviews, hotels = parse_reviews_csv(csv_content)
    assert len(reviews) == 2
    assert "Dirty room" in reviews[0]
    assert "Slow wifi" in reviews[0]
    assert hotels[0] == "London Inn"
    assert hotels[1] == "Paris Hotel"


def test_parse_full_review_column():
    csv_content = (
        "Hotel_Name,Full_Review\n"
        "Berlin Stay,Excellent breakfast and friendly staff.\n"
    ).encode("utf-8")

    reviews, hotels = parse_reviews_csv(csv_content)
    assert reviews[0] == "Excellent breakfast and friendly staff."
    assert hotels[0] == "Berlin Stay"


def test_parse_first_column_fallback():
    csv_content = "Review Text\nAmazing location near the beach.\n".encode("utf-8")
    reviews, hotels = parse_reviews_csv(csv_content)
    assert reviews[0] == "Amazing location near the beach."
    assert hotels[0] is None
