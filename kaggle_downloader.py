import os
import zipfile

def download_dataset():
    """Download the Kaggle 515k Hotel Reviews dataset."""
    print("📥 Attempting to download Kaggle dataset...")
    
    # Requirement: User must have kaggle installed and kaggle.json configured
    try:
        import kaggle
    except ImportError:
        print("❌ Error: 'kaggle' library not found. Run 'pip install kaggle'.")
        return

    dataset_slug = "jiashenliu/515k-hotel-reviews-data-in-europe"
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    try:
        kaggle.api.dataset_download_files(dataset_slug, path=raw_dir, unzip=True)
        print(f"✅ Dataset downloaded and extracted to {raw_dir}")
    except Exception as e:
        print(f"❌ Failed to download dataset: {e}")
        print("💡 Manual backup: Download 'Hotel_Reviews.csv' from Kaggle and place in data/raw/")

if __name__ == "__main__":
    download_dataset()
