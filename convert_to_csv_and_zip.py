#!/usr/bin/env python3
import pandas as pd
import zipfile
import os
from pathlib import Path

def convert_parquet_to_csv_and_zip():
    base_dir = Path("/home/gaen/usmarket_Data/US_market_computed_features/combined_by_interval")
    output_dir = Path("/home/gaen/usmarket_Data/US_market_computed_features/csv_output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    csv_files = []
    
    # Process each interval directory
    for interval_dir in base_dir.iterdir():
        if interval_dir.is_dir():
            interval_name = interval_dir.name
            parquet_file = interval_dir / f"combined_{interval_name}.parquet"
            
            if parquet_file.exists():
                print(f"Converting {parquet_file} to CSV...")
                
                # Read parquet file
                df = pd.read_parquet(parquet_file)
                
                # Save as CSV
                csv_filename = f"combined_{interval_name}.csv"
                csv_path = output_dir / csv_filename
                df.to_csv(csv_path, index=False)
                csv_files.append(csv_path)
                
                print(f"Saved {csv_filename}")
    
    # Create zip file with all CSV files
    zip_path = output_dir / "combined_features.zip"
    print(f"Creating zip file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for csv_file in csv_files:
            zipf.write(csv_file, csv_file.name)
            print(f"Added {csv_file.name} to zip")
    
    print(f"All files converted and zipped to: {zip_path}")
    
    # Optionally remove individual CSV files after zipping
    for csv_file in csv_files:
        csv_file.unlink()
        print(f"Removed {csv_file.name}")

if __name__ == "__main__":
    convert_parquet_to_csv_and_zip()