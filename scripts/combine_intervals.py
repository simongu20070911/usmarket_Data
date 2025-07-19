# SPDX-License-Identifier: MIT
"""Utility for concatenating multi-interval features and responders.

This script loads feature and responder parquet files produced by the
quantitative feature pipeline at 30s, 60s, 120s and 300s intervals.
It aligns them on the ``ts_event`` timestamp and concatenates them into
a single dataframe per day.

The directory layout is expected to match the ``US_market_computed_features``
structure shipped with this repository.
"""
from pathlib import Path
from typing import List
import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1] / "US_market_computed_features"
FEATURES_DIR = BASE_DIR / "features"
TARGETS_DIR = BASE_DIR / "targets"
OUTPUT_DIR = BASE_DIR / "combined"

INTERVALS = [30, 60, 120, 300]


def get_daily_files(interval: int) -> List[Path]:
    feature_path = FEATURES_DIR / f"{interval}s_interval" / f"final_features_{interval}s"
    return sorted(feature_path.glob("*.parquet"))


def load_interval_data(interval: int, date_file: Path) -> pl.DataFrame:
    """Load features and targets for a given interval and date."""
    date = date_file.stem
    features = pl.read_parquet(date_file)

    target_path = TARGETS_DIR / f"{interval}s" / f"target_labels_{interval}s" / f"{date}.parquet"
    if target_path.exists():
        targets = pl.read_parquet(target_path)
        features = features.join(targets, on="ts_event", how="left")
    return features


def concatenate_by_day(date: str) -> pl.DataFrame:
    """Concatenate all intervals for a single day."""
    merged = None
    for interval in INTERVALS:
        feature_file = FEATURES_DIR / f"{interval}s_interval" / f"final_features_{interval}s" / f"{date}.parquet"
        if not feature_file.exists():
            continue
        df = load_interval_data(interval, feature_file)
        suffix = f"_{interval}s"
        feature_cols = [c for c in df.columns if c != "ts_event"]
        df = df.rename({c: f"{c}{suffix}" for c in feature_cols})
        if merged is None:
            merged = df
        else:
            merged = merged.join(df, on="ts_event", how="inner")
    return merged


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    daily_files = get_daily_files(30)
    for file in daily_files:
        date = file.stem
        combined = concatenate_by_day(date)
        out_file = OUTPUT_DIR / f"combined_{date}.parquet"
        combined.write_parquet(out_file)
        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
