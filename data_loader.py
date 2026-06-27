import pandas as pd
import os
import json
from typing import List

class DataPipeline:
    """Production pipeline for cleaning and chunking the 515k dataset."""
    
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def process(self, chunk_size=5000):
        """Processes the 515k dataset in chunks to avoid OOM."""
        print(f"🚀 Starting pipeline for {self.input_file}")
        
        # Kaggle 515k dataset columns: Negative_Review, Positive_Review, Hotel_Name, etc.
        # We merge Negative and Positive into a single context for ABSA
        count = 0
        try:
            for chunk in pd.read_csv(self.input_file, chunksize=chunk_size):
                # Data Cleaning: Handle 'No Negative' or 'No Positive' entries
                chunk['Negative_Review'] = chunk['Negative_Review'].replace('No Negative', '')
                chunk['Positive_Review'] = chunk['Positive_Review'].replace('No Positive', '')
                
                # Combine reviews
                chunk['Full_Review'] = chunk['Negative_Review'] + " " + chunk['Positive_Review']
                
                # Keep relevant columns
                processed_chunk = chunk[['Hotel_Name', 'Full_Review', 'Average_Score']]
                
                output_path = os.path.join(self.output_dir, f"bulk_chunk_{count}.csv")
                processed_chunk.to_csv(output_path, index=False)
                
                print(f"✅ Processed chunk {count} ({len(chunk)} reviews)")
                count += 1
                
        except Exception as e:
            print(f"❌ Pipeline Error: {e}")

if __name__ == "__main__":
    raw_csv = "data/raw/Hotel_Reviews.csv"
    if os.path.exists(raw_csv):
        pipeline = DataPipeline(raw_csv, "data/processed")
        pipeline.process()
    else:
        print(f"⚠️ {raw_csv} not found. Run kaggle_downloader.py first.")
