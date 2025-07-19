# Parquet Data Overview

This repository contains engineered market features and target/responder labels
for multiple time intervals. Each interval (30s, 60s, 120s, 300s) is stored in a
separate directory inside `US_market_computed_features`.

## Directory layout

```
US_market_computed_features/
├── features/
│   ├── 30s_interval/
│   │   └── final_features_30s/
│   │       └── {DATE}.parquet
│   ├── 60s_interval/
│   │   └── final_features_60s/
│   │       └── {DATE}.parquet
│   ├── 120s_interval/
│   │   └── final_features_120s/
│   │       └── {DATE}.parquet
│   └── 300s_interval/
│       └── final_features_300s/
│           └── {DATE}.parquet
├── targets/
│   ├── 30s/target_labels_30s/{DATE}.parquet
│   ├── 60s/target_labels_60s/{DATE}.parquet
│   ├── 120s/target_labels_120s/{DATE}.parquet
│   └── 300s/target_labels_300s/{DATE}.parquet
```

- **Feature files** contain engineered market microstructure features as
  described in `readme.md`. They use the column `ts_event` as the timestamp.
- **Target files** store label and responder columns for the same interval,
 also keyed by `ts_event`.

## Combining intervals

The script `scripts/combine_intervals.py` demonstrates how to merge feature and
responder data from all intervals. For each trading day it:

1. Loads the daily parquet from every interval.
2. Merges the corresponding target labels on `ts_event`.
3. Renames columns with an interval suffix (e.g. `_30s`) to avoid clashes.
4. Performs an inner join across intervals on `ts_event`.
5. Writes a `combined_{DATE}.parquet` file to `US_market_computed_features/combined`.

This combined parquet aligns all features and responders by timestamp so that a
single dataframe can be used for modeling.

The script is implemented with the [Polars](https://pola.rs) library for fast
Parquet reading and writing. Ensure `polars` is available in your Python
environment before running the concatenation.

## Combining across dates

If you need a single dataset per interval that spans all available trading days,
use the companion script `scripts/combine_by_interval.py`. It:

1. Loads each daily feature parquet for the given interval.
2. Joins the matching target labels on `ts_event`.
3. Concatenates all days together using a relaxed diagonal strategy so missing
   columns are filled with nulls.
4. Writes `combined_{INTERVAL}.parquet` files under
   `US_market_computed_features/combined_by_interval/{INTERVAL}s/`.

This produces one parquet per interval containing every timestamp available,
ready for modeling or exploratory analysis.
