# Financial Risk & Volatility Monitor: Project Brief

## Phase 1 One-Page Brief

**Purpose:** Build an educational, reproducible financial risk monitor that compares a historical-variance baseline with GARCH(1,1) daily variance forecasts. The result should demonstrate original data-science work for GitHub, LinkedIn, and a resume without presenting investment advice or a trading system.

**Research question:** Can GARCH(1,1) provide more useful one-day-ahead variance forecasts than a historical-variance baseline for two liquid U.S. ETFs when both are evaluated chronologically on identical dates?

**Audience:** Junior-to-mid-level financial analysts, risk analysts, and data science reviewers who want an interpretable workflow from documented market data to measured model comparison and a small usable product.

**Version 1 scope:** Request daily data for `SPY` and `QQQ` from `2015-01-02` through `2025-12-31`, subject to source availability. The Phase 2 Step 1 Nasdaq fetch returned `2016-09-28` through `2025-12-31` for both symbols, which remains a multi-year period covering the 2020 volatility shock and 2022 equity drawdown. The project will include data validation, daily percentage returns, exploratory price/return/volatility charts, chronological one-day-ahead variance backtesting, a five-trading-day forecast, FastAPI endpoints, a small dashboard, and a measured case study. It will not include intraday data, portfolio optimization, live trading, deep learning, covariance modeling, or claims of investment suitability.

**Source and rights plan:** Use Nasdaq historical quote API responses for `SPY` and `QQQ`; record source URL, fetch timestamp, requested and returned ranges, row counts, and checksums. Stooq was the original plan, but during Phase 2 Step 1 the CSV endpoint served browser verification followed by `Access denied`, and its static bulk ZIP returned `401 Unauthorized`. Treat raw fetched data as local reproducibility artifacts and do not redistribute bulk raw market data unless source terms are confirmed to allow it. Publish source code, metadata, derived charts/metrics, and instructions for users to regenerate data locally.

**Analyst questions:** The dashboard and API should help answer: how prices and daily returns behaved over the selected period; when volatility appeared elevated and how recent volatility compares across assets; and whether the baseline or GARCH produced better chronological variance forecasts, plus the current five-trading-day forecast.

**Evaluation plan:** Compare baseline and GARCH forecasts on the same symbols, forecast origins, target dates, units, and realized proxy. The target is one-trading-day-ahead variance; the realized proxy is next-day squared daily percentage return. Use MAE as the primary metric and QLIKE as a secondary metric when forecast variances are positive. Report by symbol and overall, including sample size and test date range. GARCH is allowed to improve, tie, or underperform.

**Acceptance criteria:** The release is successful when setup is reproducible from a local Python 3.11 environment, data fetching and validation are scripted, model evaluation prevents look-ahead leakage, API/dashboard outputs are validated and clearly labeled, tests cover meaningful behavior, and the README/case study report measured findings, limitations, source attribution, and non-advice language.

**Timeline:** Phase 2 builds the data pipeline and exploratory analysis. Phase 3 implements modeling, backtesting, API, dashboard, and checks. Phase 4 turns verified results into the case study, README, release materials, and optional external publishing after explicit user approval.

**Current assumptions:** Nasdaq has usable daily OHLCV rows for both ETFs across the returned `2016-09-28` to `2025-12-31` period; exact train/test boundary and baseline window will be chosen after validated data is available; raw-data redistribution remains restricted until final rights review.

## Detailed Phase 1 Notes

## Version 1 Goal

Build an educational financial risk monitor that compares a simple historical-variance baseline with a GARCH(1,1) daily variance forecast for two liquid assets from one market. The product should help an analyst inspect recent price behavior, compare realized and forecast volatility, and request a short horizon risk forecast through both a dashboard and a FastAPI service.

This project is not investment advice, a trading strategy, or a production risk system. It is a reproducible portfolio project that demonstrates data validation, time-series feature engineering, chronological model evaluation, API design, and clear communication of limitations.

## Research Question

Can a simple GARCH(1,1) model provide more useful one-day-ahead variance forecasts than a historical-variance baseline for two liquid assets, when both models are evaluated chronologically on the same dates?

## Audience

The primary audience is a junior-to-mid-level financial analyst, risk analyst, or data science hiring reviewer who wants to see an interpretable workflow from documented market data to measured forecast comparison and a small usable product.

## Inputs

- Daily OHLCV prices for two liquid assets from one market; current returns use raw `Close` prices, not adjusted close.
- Documented symbol definitions, exchange calendar, date range, timezone, and data-source terms.
- User-selected forecast request parameters exposed by the API and dashboard after the data and modeling steps are implemented.

## Outputs

- Clean validated price and return data with provenance metadata.
- Exploratory charts for prices, returns, distributions, and rolling volatility.
- Chronological backtest comparing historical variance and GARCH(1,1) variance forecasts.
- Five-trading-day variance and volatility forecast view.
- FastAPI endpoints for health checks, available symbols, and forecast requests.
- Dashboard views that summarize recent risk behavior and model outputs.
- A short case study with measured findings and limitations.

## Version 1 Scope

Version 1 will focus on two assets in one market, daily prices, daily percentage returns, one-day-ahead variance backtesting, and a five-trading-day forecast. It will avoid portfolio optimization, intraday data, live trading signals, deep learning, macro features, and multi-asset covariance modeling.

## Assets and Period

Version 1 will use two U.S.-listed exchange-traded funds:

| Symbol | Name | Market / listing | Exposure represented | Project role |
| --- | --- | --- | --- | --- |
| `SPY` | SPDR S&P 500 ETF Trust | NYSE Arca, USD | Broad U.S. large-cap equity exposure through the S&P 500 Index | Broad-market reference asset |
| `QQQ` | Invesco QQQ Trust, Series 1 | Nasdaq, USD | Nasdaq-100 equity exposure, excluding most financial companies | Growth/technology-tilted comparison asset |

The requested analysis period is daily data from **2015-01-02 through 2025-12-31**, subject to final data availability from the selected source. The Phase 2 Step 1 Nasdaq fetch returned **2016-09-28 through 2025-12-31** for both symbols. This returned period is long enough to include calm markets, the 2020 COVID-19 volatility shock, the 2022 equity drawdown, and the later recovery period, while keeping the project manageable for a first release.

Calendar assumptions:

- Frequency: daily trading sessions only; weekends and U.S. market holidays are excluded.
- Primary calendar: U.S. equity-market trading calendar aligned to NYSE/Nasdaq regular sessions.
- Timezone: U.S. Eastern time for exchange-session interpretation; stored daily dates should be timezone-naive calendar dates after validation.
- Early closes: treated as valid trading sessions because daily closing prices are still produced.
- Missing sessions: documented and validated in the data-quality step before returns are calculated.

Selection rationale:

- `SPY` and `QQQ` are liquid, widely recognized ETFs with long histories and public symbol definitions.
- Both trade in the U.S. market, keeping calendar and currency handling simple for version 1.
- Their return behavior should be similar enough for a fair workflow comparison but different enough to make the volatility views informative.
- ETFs avoid single-company event risk dominating the first release.

## Data Source and Rights

Planned source after Phase 2 Step 1 source check: **Nasdaq historical quote API**.

Stooq was selected during Phase 1 as the preferred source, but the planned CSV endpoint returned a JavaScript browser-verification page and then `Access denied` during Phase 2 Step 1. The Stooq static bulk daily ZIP also returned `401 Unauthorized`. Yahoo Finance was tested as a fallback and returned `Too Many Requests`. Nasdaq's historical quote endpoint returned usable daily OHLCV rows for the selected ETFs, so the implementation uses Nasdaq for version 1 unless a later rights review requires another source.

Access method:

- Use Nasdaq's historical quote API endpoint for each symbol and date range.
- Planned URL pattern: `https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=etf&fromdate=YYYY-MM-DD&todate=YYYY-MM-DD&limit=9999`
- Planned project symbols: `SPY` and `QQQ`.
- Requested date parameters: `fromdate=2015-01-02` and `todate=2025-12-31`.
- Phase 2 Step 1 returned rows from `2016-09-28` through `2025-12-31` for both project symbols.
- Fetching is implemented in a repeatable script at `scripts/fetch_prices.py`.

Expected source fields:

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

Adjustment and price choice:

- The initial modeling input will use daily `Close` because the Nasdaq endpoint returns OHLCV fields but not a clearly documented adjusted-close field in the fetched response.
- Any split/dividend adjustment limitations observed in the fetched files will be documented before returns are calculated.
- The project will treat returns as close-to-close price returns, not dividend-adjusted or total returns, unless a later approved source change provides a documented adjusted-close series.
- If the selected source cannot support an adjusted close with acceptable documentation, the project will state that limitation and avoid overstating comparability across long horizons.

Timestamp and reproducibility:

- Source choice documented on **2026-09-29**.
- Each fetch will record the UTC fetch timestamp, source URL, symbol, requested date range, row count, first date, last date, and file checksum.
- Raw fetched files should be treated as local reproducibility artifacts, not polished published outputs.

Timezone and calendar:

- Nasdaq daily rows will be interpreted as exchange-session dates for U.S. equities.
- The project will align expected sessions to the U.S. equity trading calendar and document gaps during validation.
- Dates will be stored as calendar dates after validation; intraday timestamps are out of scope for version 1.

Sharing and publication terms:

- The public repository should include source code, metadata, documentation, and small derived examples only when allowed.
- The project should not redistribute bulk raw market data unless source terms are reviewed and recorded as allowing that use.
- The README and case study should cite Nasdaq as the data source and instruct users to regenerate data locally with the documented script.
- Charts and metrics may be published as derived educational outputs with source attribution, subject to final rights review before release.

Fallback source:

- If Nasdaq availability, access, or rights become unsuitable, select a replacement source only after documenting its terms and accepting any access or licensing restrictions.

## Success Criteria and Evaluation Plan

Version 1 succeeds if it produces a reproducible, inspectable risk-monitor workflow with honest evidence, even if GARCH(1,1) does not outperform the baseline.

Functional acceptance checks:

- Project setup can be recreated from documented commands in a local virtual environment.
- Price fetching uses a repeatable script that records source URL, fetch timestamp, symbol, requested range, returned range, row count, and checksum.
- Data validation catches duplicate dates, non-chronological rows, missing required fields, nonpositive prices, and unexpected gaps relative to the selected market calendar.
- Return calculation uses daily percentage returns with explicit units and drops only the first missing return per symbol unless validation justifies additional removals.
- Exploratory outputs include price, return, distribution, and 20-/50-day rolling-volatility charts with titles, units, source, symbols, and date range.
- Backtesting uses chronological train/test separation so each forecast origin uses only data available before the target date.
- The baseline and GARCH models are evaluated on identical symbols, target dates, return units, and realized-variance proxy.
- Forecast variance values are positive before QLIKE is computed; invalid or nonpositive forecasts are handled explicitly rather than silently scored.
- API endpoints `GET /health`, `GET /symbols`, and `POST /forecast` return validated request/response models and clear error messages.
- Dashboard views answer the three analyst questions documented above and label variance separately from volatility.
- README and case study report measured results, data source, limitations, and non-advice language.

Model evaluation design:

- Split: choose a fixed chronological train/test boundary after data validation, with the exact boundary recorded before model scoring.
- Forecast target: one-trading-day-ahead conditional variance for each symbol.
- Realized proxy: next trading day's squared daily percentage return, documented as a noisy proxy for realized variance.
- Baseline: rolling historical variance using only prior returns. The window length will be selected in the modeling step and recorded before final comparison.
- GARCH model: GARCH(1,1) fit with the `arch` package using only prior returns at each forecast origin or an explicitly documented expanding-window process.
- Shared scoring sample: compare both models only on dates where both produce valid forecasts and the realized proxy is available.
- Primary metric: mean absolute error between forecast variance and next-day squared return.
- Secondary metric: QLIKE when all included forecast variances are positive, because it is commonly used for volatility-forecast comparison and penalizes scale errors differently from MAE.
- Reporting: show metrics by symbol and overall, include sample size and test date range, and report whether GARCH improves, ties, or underperforms the baseline.

Fairness rules:

- Do not tune the test period after seeing model results.
- Do not change the baseline window only to make GARCH look better.
- Do not drop difficult market periods unless a documented data-quality issue requires it.
- Do not claim that lower forecast error proves tradable alpha, portfolio improvement, or investment suitability.
- If GARCH underperforms the baseline, report that result plainly and use it as part of the case study.

Minimum quality bar for release:

- All documented commands for setup, data preparation, tests, API startup, and dashboard startup run successfully from a clean local checkout.
- Tests cover data order, leakage prevention, forecast positivity, request validation, and at least one end-to-end forecast path.
- Case-study charts and metrics are regenerated from project scripts, not manually edited.
- Publication review confirms raw-data sharing choices, source attribution, and absence of secrets or nonredistributable course material.

## Analyst Questions and Product Mapping

### Question 1: How have prices and daily returns behaved over the selected period?

An analyst should be able to identify the broad price path, periods of large daily moves, and whether returns appear centered with heavy tails or outliers.

Dashboard mapping:

- Price chart by symbol with date range, units, and source label.
- Daily return chart by symbol using percentage-return units.
- Return distribution chart that highlights spread and outliers without implying a normal distribution unless tested.

API mapping:

- No dedicated API response is required for exploratory charts in version 1.
- `GET /symbols` should provide the available symbols and metadata needed for the dashboard to label these views correctly.

### Question 2: When did volatility appear elevated, and how does recent volatility compare across the two assets?

An analyst should be able to inspect 20-day and 50-day rolling volatility, compare the two assets on the same units, and connect elevated volatility periods to observed return behavior without claiming causality.

Dashboard mapping:

- Rolling volatility chart with 20-day and 50-day windows for each symbol.
- Summary panel showing latest available rolling volatility values, date of latest observation, and data coverage.
- Data-quality/provenance note showing the source, adjustment choice, and known missing-session handling.

API mapping:

- `GET /symbols` should include enough symbol metadata and latest data date for the dashboard summary.
- Forecast endpoints should report the training cutoff or latest source date so users know what information the forecast used.

### Question 3: Which variance forecast was more accurate in chronological backtesting, and what is the short-term forecast now?

An analyst should be able to compare the historical-variance baseline and GARCH(1,1) on identical forecast dates, understand the metric used, and request a five-trading-day forecast with variance and volatility units clearly separated.

Dashboard mapping:

- Model comparison panel with identical test dates, sample size, and metrics such as MAE and QLIKE when valid.
- Forecast table or chart for the next five trading days showing forecast variance and forecast volatility separately.
- Plain-language limitation note explaining that squared next-day returns are a noisy realized-variance proxy.

API mapping:

- `POST /forecast` should accept a valid symbol and forecast horizon, then return forecast variance, forecast volatility, units, model name, training cutoff, and source-data timestamp.
- `GET /health` should confirm service availability.
- `GET /symbols` should list forecastable symbols and their display names.

## Current Assumptions

- Nasdaq returned daily `SPY` and `QQQ` rows from `2016-09-28` through `2025-12-31`; date continuity and gaps will be verified in Phase 2 Step 2.
- The exact train/test boundary and baseline variance window will be chosen later after validated data is available, then recorded before scoring.
- Repository scaffolding, dependency management, data fetching, modeling, API implementation, and dashboard implementation are intentionally deferred to later approved steps.

## References Checked for Asset and Calendar Definitions

- State Street describes `SPY` as the SPDR S&P 500 ETF Trust listed on NYSE Arca with ticker `SPY`.
- Invesco describes `QQQ` as the Invesco QQQ ETF / Invesco QQQ Trust linked to the Nasdaq-100 Index with fund ticker `QQQ`.
- NYSE publishes official holidays and trading-hours calendars for NYSE markets, including NYSE Arca equities.
- Stooq exposes historical daily market data through downloadable CSV-style URLs and bulk historical files, but access was blocked during Phase 2 Step 1.
- Yahoo Finance documents that historical-data download access can require a Gold subscription and can be restricted for some instruments because of data licensing.
- Nasdaq exposes historical quote rows through its quote API and returned usable OHLCV rows during Phase 2 Step 1 source testing.
