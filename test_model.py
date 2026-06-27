from app.ml_engine import ml_engine
import json

def test_inference():
    # Test cases representing different hotel aspects
    reviews = [
        "The staff was incredibly helpful and the room was spotless. However, the breakfast was a bit cold.",
        "Beautiful location right by the beach, but the Wi-Fi was terrible and the staff seemed disinterested.",
        "Great value for money. The cleanliness was top-notch, though the food was just average."
    ]

    print("--- 🏨 Hotel Intelligence: ABSA Local Test ---")
    for review in reviews:
        print(f"\nReview: {review}")
        results = ml_engine.analyze(review)
        for res in results:
            print(f"  > Aspect: {res.aspect:12} | Sentiment: {res.sentiment:10} | Score: {res.score:.4f}")

if __name__ == "__main__":
    try:
        test_inference()
    except Exception as e:
        print(f"Error during test: {e}")
        print("Note: Ensure 'transformers' and 'torch' are installed (pip install transformers torch).")


        