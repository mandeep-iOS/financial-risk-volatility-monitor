# Data Provenance and Freshness

The project uses Nasdaq historical OHLCV snapshots stored under `data/raw/` and a validated SQLite store under `data/processed/`. Generated metadata under `data/metadata/` records validation, return calculation, volatility, forecast, scoring, and evaluation provenance.

The current validated snapshot covers SPY and QQQ through 2025-12-31. The API and frontend expose that boundary rather than implying live data.

Forecast freshness is defined by the latest available price date compared with the current date. When the artifact is stale, the response and UI use `forecast_status: historical/example` and `is_current: false`. Model training cutoff, forecast generation timestamp, and forecast date range remain visible so a reviewer can distinguish historical example output from a live service.

Raw close returns are intentional for this educational project. A production workflow should document adjusted prices, corporate actions, source credentials, refresh scheduling, and failure monitoring more fully.
