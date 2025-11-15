


The `ts_event` column is the primary timestamp index for all aggregated feature dataframes. It represents the **start of the time interval** (the "open" of the bar). The intervals are left-closed and right-open.

-   **Example:** For a `30s` interval, a `ts_event` of `2025-03-19 09:30:00.000` represents the aggregation of all raw data that occurred from `09:30:00.000` up to (but not including) `09:30:30.000`.

### Naming Convention

All feature columns follow a standardized naming convention to ensure clarity and avoid ambiguity:

`[FeatureName]_[Interval]_[InstrumentSuffix]`

-   **`[FeatureName]`**: The base name of the feature (e.g., `realized_vol`, `net_gamma_flow`).
-   **`[Interval]`**: The aggregation interval in seconds (e.g., `30s`, `60s`).
-   **`[InstrumentSuffix]`**: The suffix of the instrument the feature was calculated for (e.g., `_spy`, `_qqq`, `_spxw`).

**Example:** `realized_vol_30s_spy` is the realized volatility for SPY, calculated over a 30-second interval.

### Raw Data Granularity (OHLCV)

The raw data for futures instruments (`_mes`, `_mnq`) is provided as 1-second OHLCV bars. When these are used for feature calculation:
-   The **`close`** price of the 1-second bar is treated as the primary `price` for that second.
-   The **`volume`** of the 1-second bar is treated as the `size` for that second.
-   Bid/Ask prices for futures are proxied using the `close` price and the configured `tick_size` if available.

## 3. Feature Categories

### I. Core Market Microstructure Features (Single-Asset)

These features are calculated for each individual underlying asset (ETFs and Futures).

| Feature Name (Base)     | Example Column Name                | Description                                                                                                                                                                                                                                        |
| ----------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log_mid_price`         | `log_mid_price_30s_spy`            | The natural logarithm of the last known mid-price (average of best bid and ask) at the end of the interval. For OHLCV data, this is the log of the last `close` price.                                                                                   |
| `micro_price`           | `micro_price_30s_spy`              | The order book imbalance-adjusted price at the end of the interval. Formula: `(Bid * AskSize + Ask * BidSize) / (BidSize + AskSize)`. Falls back to the mid-price if depth information is unavailable.                                                     |
| `spread_pct`            | `spread_pct_30s_spy`               | The bid-ask spread as a percentage of the mid-price at the end of the interval. Formula: `(Ask - Bid) / MidPrice`. For OHLCV data with a `tick_size`, this is `tick_size / last_close_price`.                                                           |
| `depth_ratio`           | `depth_ratio_30s_spy`              | The ratio of bid-side depth to total depth at the best level at the end of the interval. Formula: `BidSize / (BidSize + AskSize)`.                                                                                                                   |
| `volume`                | `volume_30s_spy`                   | The total number of shares/contracts traded during the interval.                                                                                                                                                                                   |
| `trade_count`           | `trade_count_30s_spy`              | The total number of trades that occurred during the interval.                                                                                                                                                                                      |
| `signed_volume`         | `signed_volume_30s_spy`            | The sum of trade volumes, signed based on trade price relative to the prevailing bid/ask spread (Lee-Ready algorithm). Positive indicates buyer-initiated, negative indicates seller-initiated. For OHLCV, it is signed by the direction of the price change. |
| `ofi` (Order Flow Imbalance) | `ofi_30s_spy`                      | A proxy for order flow imbalance based on changes in best bid/ask depth. Positive indicates more buying pressure. Formula: `Δ(BidSize) - Δ(AskSize)`.                                                                                                    |
| `vwap_deviation`        | `vwap_deviation_30s_spy`           | The deviation of the interval's Volume-Weighted Average Price (VWAP) from the interval's last mid-price. Formula: `(VWAP - MidPrice) / MidPrice`.                                                                                                  |
| `realized_vol`          | `realized_vol_30s_spy`             | Annualized realized volatility, calculated as the square root of the sum of squared tick-level log returns within the interval.                                                                                                                   |
| `bipower_var`           | `bipower_var_30s_spy`              | Annualized bipower variation, a jump-robust measure of integrated variance. It is less sensitive to large price jumps than `realized_vol`.                                                                                                         |
| `interval_log_return`   | `interval_log_return_30s_spy`      | The total log return over the interval, calculated as the sum of all tick-level log returns.                                                                                                                                                           |
| `vpin`                  | `vpin_spy`                         | The Volume-Synchronized Probability of Informed Trading. This is a bucket-based calculation and is forward-filled onto the time grid. A higher VPIN suggests a higher probability of order flow toxicity.                                               |

### II. Option-Specific Features (`_spxw`)

These features are calculated from the SPXW option chain and aggregated to the interval grid.

| Feature Name (Base)        | Example Column Name                     | Description                                                                                                                                                                                                                             |
| -------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `iv_atm`                   | `iv_atm_30s_spxw`                       | The Implied Volatility (IV) of the at-the-money (ATM) option, interpolated from the two options with strikes closest to the underlying's price.                                                                                                |
| `iv_rr25` (Risk Reversal)  | `iv_rr25_30s_spxw`                      | The 25-delta risk reversal, a measure of volatility skew. Calculated as the difference between the IV of a 25-delta call and a 25-delta put. A positive value indicates calls are more expensive (demand for upside).                          |
| `iv_slope`                 | `iv_slope_30s_spxw`                     | The slope of the IV smile, calculated between two delta points (e.g., 10-delta and 40-delta options). Measures how steeply IV changes with respect to the strike price.                                                                    |
| `skew_index`               | `skew_index_30s_spxw`                   | An index similar to the CBOE SKEW index, calculated from the difference in IV between OTM puts and OTM calls (e.g., 10-delta). It measures the perceived risk of a tail-event (black swan).                                                      |
| `net_delta_flow`           | `net_delta_flow_30s_spxw`               | The net delta exposure of traded options during the interval. It is the sum of `(signed_trade_volume * delta)` for each option trade. Measures the net directional positioning from option market activity.                                      |
| `net_gamma_flow`           | `net_gamma_flow_30s_spxw`               | The net gamma exposure of traded options. Sum of `(signed_trade_volume * gamma)`. Measures the change in market makers' delta hedging requirements.                                                                                         |
| `net_vega_flow`            | `net_vega_flow_30s_spxw`                | The net vega exposure of traded options. Sum of `(signed_trade_volume * vega)`. Measures the net positioning on changes in implied volatility.                                                                                             |
| `option_ofi`               | `option_ofi_30s_spxw`                   | The Order Flow Imbalance summed across all options in the chain.                                                                                                                                                                        |
| `option_spread_pct_vw`     | `option_spread_pct_vw_30s_spxw`         | The volume-weighted average of the bid-ask spread percentage across all traded options in the interval. A measure of the average liquidity cost for options.                                                                                |
| `option_vwap_deviation`    | `option_vwap_deviation_30s_spxw`        | The deviation of the volume-weighted average price of all traded options from the price of the at-the-money straddle.                                                                                                                       |

### III. Cross-Asset & Interaction Features

These features capture relationships between different assets.

| Feature Name (Base)           | Example Column Name                 | Description                                                                                                                                                                                                                                      |
| ----------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `basis_mes_spy`               | `basis_mes_spy_30s`                 | The price difference (basis) between the MES futures contract and the SPY ETF, after scaling the futures price. Formula: `(MES_LastPrice / ScaleFactor) - SPY_VWAP`.                                                                                  |
| `basis_mnq_qqq`               | `basis_mnq_qqq_30s`                 | The price difference (basis) between the MNQ futures contract and the QQQ ETF, after scaling. Formula: `(MNQ_LastPrice / ScaleFactor) - QQQ_VWAP`.                                                                                                  |
| `lagged_corr_spy_mes_1`       | `lagged_corr_spy_mes_1_30s`         | The rolling correlation between SPY returns and MES returns from the previous interval (lag=1).                                                                                                                                                  |
| `ofi_spread_spy_mes`          | `ofi_spread_spy_mes_30s`            | The difference in Order Flow Imbalance between SPY and MES.                                                                                                                                                                                      |
| `vol_hedge_spread`            | `vol_hedge_spread_30s`              | A synthetic volatility hedge spread. Formula: `(SPY_Price + 0.5 * QQQ_Price) - VXX_Price`.                                                                                                                                                            |
| `iv_rv_spread`                | `iv_rv_spread_30s`                  | The spread between implied volatility (from SPXW options) and realized volatility (from SPY ETF). A key measure of the volatility risk premium. Formula: `iv_atm_spxw - realized_vol_spy`.                                                           |
| `gamma_participation`         | `gamma_participation_30s`           | Measures the notional gamma flow from options relative to the notional volume traded in the underlying ETF. Indicates the relative impact of gamma hedging on underlying market activity.                                                            |
| `delta_drift`                 | `delta_drift_30s`                   | Measures the "unexplained" net delta flow from options after accounting for the expected delta change due to the underlying's price movement. Indicates new directional positioning.                                                               |
| `skew_return_interaction`     | `skew_return_interaction_30s`       | The product of the change in volatility skew (`Δiv_rr25`) and the underlying's log return. Captures the dynamic relationship between skew and price moves (e.g., "crash-o-phobia").                                                              |

### IV. Machine Learning & Fused Features

These features are generated by neural network models and represent learned, compressed representations of the market state.

| Feature Prefix    | Example Column Name | Description                                                                                                                                                                                                                                      |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `z_`              | `z_0`, `z_1`, ...   | A latent space embedding from a Temporal Convolutional Network (TCN) Autoencoder or VAE. It is a compressed, 32-dimensional representation of the state of 12 high-frequency features (ETF prices, spreads, option IVs, etc.) over the last 60 seconds. These features are generated at a 200ms frequency but are aligned to the main interval grids for concatenation. |
| `fused_feat_`     | `fused_feat_0`      | A 96-dimensional feature vector resulting from a cross-attention mechanism. It fuses the `z_*` embeddings with the entire set of lower-frequency (e.g., 30s) engineered features (Categories I, II, III). It represents a learned combination of high-frequency and low-frequency information. |

### V. Target & Responder Features (Labels for ML)

These columns are the "answers" or labels that a machine learning model would be trained to predict. They are calculated based on future data relative to the current `ts_event`.

| Feature Name (Base)                          | Description                                                                                                                                                                                                                                         |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target_next_window_return`                  | The log return of the primary underlying (SPY) over the next interval, adjusted for a small transaction cost estimate.                                                                                                                              |
| `target_next_iv_rv_spread`                   | The value of the `iv_rv_spread` in the next interval.                                                                                                                                                                                               |
| `target_next_rv_change_regr`                 | The raw change in `realized_vol_spy` in the next interval (Regression target). Formula: `RV_t+1 - RV_t`.                                                                                                                                              |
| `target_next_rv_change_class`                | A classification target (-1, 0, 1) based on whether `realized_vol_spy` increased, decreased, or stayed the same in the next interval.                                                                                                                |
| `target_next_qqq_spy_spread_change_regr`     | The raw change in the `log(QQQ) - log(SPY)` spread in the next interval (Regression target).                                                                                                                                                       |
| `target_next_qqq_spy_spread_change_class`    | A classification target (-1, 0, 1) for the change in the QQQ-SPY spread.                                                                                                                                                                            |
| `target_next_spy_qqq_vxx_spread_change_regr` | The raw change in the `vol_hedge_spread` in the next interval (Regression target).                                                                                                                                                                  |
| `target_next_spy_qqq_vxx_spread_change_class` | A classification target (-1, 0, 1) for the change in the `vol_hedge_spread`.                                                                                                                                                                        |
| `resp_mid_*` / `resp_vwap_*`                 | **Responder Features**. These are very short-term (e.g., 30s vs 5s) log returns of either mid-price or VWAP for SPY, QQQ, and VXX. They are calculated on a finer 1-second grid and are designed to be targets for high-frequency prediction models. |

## 4. Final Output Dataframe

The final output `features_{DATE}_{INTERVAL}s.parquet` file combines one set of features with the target labels. The choice of features is controlled by the `use_tcn_concatenation` flag in the configuration:

-   **If `True` (default):** The dataframe contains `ts_event`, all engineered features (Categories I, II, III), the `z_*` embeddings, and all target features (Category V). This is the "HF Concatenated" output.
-   **If `False`:** The dataframe contains `ts_event`, all engineered features (Categories I, II, III), the `fused_feat_*` features, and all target features (Category V). This is the "Attention-Fused" output.
