from app import models, database
from app.core.security import hash_password
from app.ml_engine import ml_engine

DEMO_EMAIL = "demo@hotel.com"
DEMO_PASSWORD = "demopass123"


def seed_intelligence():
    """Generates demo user and 500 realistic reviews for dashboard testing."""
    print("Initializing Intelligence Seeder...")
    db = database.SessionLocal()

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
        print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

    sample_templates = [
        "The staff at {hotel} were amazing. Wi-Fi was fast, but the food was cold.",
        "Dirty rooms and slow check-in. The location was the only good part of staying at {hotel}.",
        "Excellent value for money. Spotless bathroom and the staff were very polite. The internet connection was weak though.",
        "Average stay. The restaurant breakfast was great, but the service at the desk was poor.",
        "Best hotel ever! Everything from the Wi-Fi speed to the cleanliness was perfect.",
    ]

    hotels = ["London Luxury Inn", "Paris Petit Hotel", "Berlin Budget Stay", "NYC Night Palace"]

    print(f"Generating data for {len(hotels)} hotels...")

    for count in range(500):
        hotel = hotels[count % len(hotels)]
        template = sample_templates[count % len(sample_templates)]
        text = template.format(hotel=hotel)

        sentiments = ml_engine.analyze(text)

        new_review = models.ReviewRecord(text=text, hotel_name=hotel, user_id=user.id)
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

        if count % 100 == 0:
            print(f"Processed {count} entries...")

    db.commit()
    db.close()
    print("Intelligence Seeder Complete. Dashboard is now ready with data!")


if __name__ == "__main__":
    seed_intelligence()
