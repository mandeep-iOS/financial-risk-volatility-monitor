# Recruiter-Facing Assets

## Résumé Project Bullets

- Built a universal SwiftUI iOS/macOS financial risk dashboard backed by Python/FastAPI for SPY and QQQ, combining symbol-aware price, volatility, drawdown, forecast, and model-evidence workflows.
- Implemented an expanding-window baseline versus GARCH(1,1) evaluation with MAE and QLIKE scoring over 932 out-of-sample targets.
- Designed a native premium fintech dashboard with Swift Charts, explicit data freshness, stale-forecast warnings, date controls, scenario analysis, and reusable Codable API contracts.

## LinkedIn Project Description

Built Financial Risk & Volatility Monitor, a native SwiftUI iOS/macOS analytics product powered by a Python/FastAPI data science backend. The app compares rolling historical variance with GARCH(1,1), visualizes returns, volatility, drawdowns, and forecasts, and makes data freshness explicit so historical estimates are never presented as live market guidance. Swift Charts powers the native dashboard while React remains an optional web reference.

## GitHub Repository Description

Native SwiftUI iOS/macOS financial risk dashboard powered by Python/FastAPI and GARCH modeling for SPY and QQQ, with explicit freshness and model evidence.

## Recommended GitHub Topics

`swiftui`, `ios`, `macos`, `python`, `fastapi`, `data-science`, `finance`, `garch`, `swift-charts`

## Short Demo Script

1. Open Overview and switch SPY to QQQ to show symbol-aware KPI and chart updates.
2. Point out the prices-through date and historical/example status pill.
3. Open Compare, adjust the date range, and explain normalized growth, volatility, and drawdown together.
4. Open Forecast and show the training cutoff, generated timestamp, forecast window, and selected-symbol forecast.
5. Open Model Evidence, explain MAE and QLIKE in one sentence each, then show the per-symbol GARCH comparison.
6. Expand technical diagnostics only after the user-facing evidence is clear.
