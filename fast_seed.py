from app import database, models
from app.core.security import hash_password

DEMO_EMAIL = "demo@hotel.com"
DEMO_PASSWORD = "demopass123"


def main() -> None:
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == DEMO_EMAIL).first()
        if not user:
            user = models.User(
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name="Demo Manager",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        existing_reviews = db.query(models.ReviewRecord).filter(models.ReviewRecord.user_id == user.id).count()
        if existing_reviews > 0:
            print(f"Demo data already exists: {existing_reviews} reviews")
            print(f"Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
            return

        samples = [
            (
                "London Luxury Inn",
                "The staff were amazing and the room was spotless.",
                [("Staff", "POSITIVE", 0.93), ("Cleanliness", "POSITIVE", 0.91)],
            ),
            (
                "Paris Petit Hotel",
                "The breakfast was cold and the wifi connection was slow.",
                [("Food", "NEGATIVE", 0.88), ("WiFi", "NEGATIVE", 0.86)],
            ),
            (
                "Berlin Budget Stay",
                "Great value for money but the bathroom was dirty.",
                [("Value", "POSITIVE", 0.90), ("Cleanliness", "NEGATIVE", 0.84)],
            ),
            (
                "NYC Night Palace",
                "Excellent location and friendly service at the front desk.",
                [("Location", "POSITIVE", 0.92), ("Staff", "POSITIVE", 0.89)],
            ),
        ]

        for index in range(40):
            hotel, text, sentiments = samples[index % len(samples)]
            review = models.ReviewRecord(text=text, hotel_name=hotel, user_id=user.id)
            db.add(review)
            db.flush()

            for aspect, sentiment, score in sentiments:
                db.add(
                    models.AspectSentiment(
                        review_id=review.id,
                        aspect=aspect,
                        sentiment=sentiment,
                        score=score,
                    )
                )

        db.commit()
        print("Fast demo seed complete")
        print(f"Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()