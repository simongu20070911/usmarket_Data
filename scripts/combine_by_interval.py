# SPDX-License-Identifier: MIT
"""Concatenate features and targets across all dates for each interval.

This script loads daily parquet files for a specific interval (30s, 60s, 120s,
300s). For each date it merges the feature file with its corresponding target
labels on ``ts_event`` and then appends the result to a single dataframe.

The output consists of one parquet per interval located in
``US_market_computed_features/combined_by_interval/{interval}s``.
"""
from pathlib import Path
from typing import List
import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1] / "US_market_computed_features"
FEATURES_DIR = BASE_DIR / "features"
TARGETS_DIR = BASE_DIR / "targets"
OUTPUT_DIR = BASE_DIR / "combined_by_interval"

INTERVALS = [30, 60, 120, 300]


def daily_files(interval: int) -> List[Path]:
    feature_path = FEATURES_DIR / f"{interval}s_interval" / f"final_features_{interval}s"
    return sorted(feature_path.glob("*.parquet"))


def load_day(interval: int, file: Path) -> pl.DataFrame:
    """Load feature and target data for a single day."""
    date = file.stem
    df = pl.read_parquet(file)
    target = TARGETS_DIR / f"{interval}s" / f"target_labels_{interval}s" / f"{date}.parquet"
    if target.exists():
        tgt_df = pl.read_parquet(target)
        df = df.join(tgt_df, on="ts_event", how="left")
    return df


def concatenate_interval(interval: int) -> pl.DataFrame:
    frames = [load_day(interval, f) for f in daily_files(interval)]
    if not frames:
        return pl.DataFrame()
    # Use diagonal_relaxed concatenation so missing columns are filled with nulls
    # and differing dtypes are coerced to a common supertype.
    return pl.concat(frames, how="diagonal_relaxed")


def main() -> None:
    for interval in INTERVALS:
        df = concatenate_interval(interval)
        if df.is_empty():
            continue
        out_dir = OUTPUT_DIR / f"{interval}s"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"combined_{interval}s.parquet"
        df.write_parquet(out_file)
        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
