# Financial Risk & Volatility Monitor: Case Study

## Problem

Financial risk dashboards often expose model outputs without helping a user understand the asset, comparison window, data freshness, or evidence behind the estimate. The goal was to turn a volatility-modeling project into a practical product for analysts and non-specialist reviewers.

## Dataset

The project uses daily Nasdaq historical OHLCV snapshots for SPY and QQQ. The validated project range is 2016-09-28 through 2025-12-31 with 2,328 rows per symbol. Returns are calculated from raw close values, and the pipeline stores prices, returns, volatility outputs, forecasts, scores, and provenance metadata locally.

## Approach

The pipeline calculates daily close returns, rolling realized volatility, running-peak drawdowns, and a five-session forecast. Forecasts are compared against a 20-session historical-variance baseline and a GARCH(1,1) model using an expanding-window out-of-sample evaluation.

The product architecture separates data access from presentation. `dashboard_data.py` provides symbol-aware loaders and a freshness contract. Python remains the data science and GARCH engine, FastAPI exposes typed JSON contracts, and the primary iOS/macOS user experience is built in SwiftUI with Swift Charts. React remains an optional web reference/fallback, while Streamlit is retained as a legacy prototype.

## Model Comparison

The evaluation window is 2024-02-23 through 2025-12-31 with 932 target rows total and 466 rows per symbol. MAE measures average forecast miss size. QLIKE evaluates variance scale forecasts and excludes non-positive realized or forecast variance rows.

Stored results show GARCH has lower MAE and QLIKE than the baseline for both SPY and QQQ in this evaluation artifact. This is a historical result for the defined split, not a claim that GARCH will always perform better.

## Product Design

The primary interface was rebuilt as a universal SwiftUI iOS/macOS dashboard to match a premium fintech SaaS reference direction. The visual system uses a dark navy canvas, branded navigation rail, compact KPI cards, native Swift Charts, blue/cyan primary accents, orange risk accents, dark chart panels, explicit status pills, and dense above-the-fold information hierarchy. This creates a stronger native portfolio artifact while preserving a React web reference.

The four product questions map to four sections: Overview, Compare, Forecast, and Model Evidence.

## Results

- Selected-symbol behavior is preserved across Overview and Forecast.
- Compare exposes normalized growth, drawdown, and summary risk metrics for SPY and QQQ.
- Forecast pages explicitly show training cutoff, generation time, date range, and historical/example status.
- Model Evidence exposes MAE, QLIKE, sample size, evaluation dates, per-symbol winners, and technical diagnostics.
- The final frontend and backend pass the project verification suite.

## Limitations

The data snapshot is historical and ends on 2025-12-31. Raw-close returns do not provide a complete adjusted-price treatment. The model comparison is one evaluation design over two ETFs and should not be generalized as investment advice or universal model superiority. Production deployment would require a managed data refresh, monitoring, authentication, and more extensive browser/accessibility testing.

## What I Learned

The hardest part was not fitting a model; it was making the model legible. A freshness contract, symbol-aware data layer, honest status language, and clear evidence page were as important to the product as the forecast calculation itself. Moving the primary UI to SwiftUI made the product feel native on both iOS and macOS while keeping networking, Codable models, responsive layouts, and native chart interactions in one shared codebase.

## Future Improvements

- Add scheduled data refresh and observable pipeline health.
- Add adjusted-price and corporate-action handling.
- Add richer forecast uncertainty calibration and additional baselines.
- Add Playwright screenshot regression and accessibility coverage.
- Add deployment configuration, authentication, and production observability.
- Add TestFlight/macOS distribution configuration and a hosted HTTPS API for physical-device demos.
