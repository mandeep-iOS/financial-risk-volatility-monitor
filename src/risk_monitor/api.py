"""FastAPI service for the educational risk monitor."""

from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from risk_monitor.config import ASSETS, DATABASE_PATH, FIGURES_DIR, METADATA_DIR
from risk_monitor.dashboard_data import (
    calculate_scenarios,
    compare_assets,
    load_dashboard_data,
    load_freshness,
    load_prices,
    summarize_asset,
)
from risk_monitor.forecast import create_five_day_forecast
from risk_monitor.volatility import load_returns

app = FastAPI(title="Financial Risk & Volatility Monitor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    service: str


class SymbolResponse(BaseModel):
    symbol: str
    name: str
    market: str


class ForecastRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    horizon: int = Field(default=5, ge=1, le=5)


class ForecastItem(BaseModel):
    forecast_date: date
    horizon: int
    model: str
    variance_pct2: float = Field(ge=0)
    volatility_pct: float = Field(ge=0)
    training_end_date: date


class ForecastFreshness(BaseModel):
    latest_available_price_date: date
    model_training_cutoff: date
    forecast_generated_at_utc: datetime
    forecast_start_date: date
    forecast_end_date: date
    forecast_status: str
    is_current: bool


class ForecastResponse(BaseModel):
    symbol: str
    horizon: int
    variance_units: str
    volatility_units: str
    forecasts: list[ForecastItem]
    freshness: ForecastFreshness


class OverviewPoint(BaseModel):
    date: date
    close: float
    volatility_20d: float | None
    return_pct: float | None


class OverviewSummary(BaseModel):
    latest_close: float
    latest_price_date: date
    recent_5d_return_pct: float
    recent_20d_return_pct: float
    volatility_20d_pct: float
    volatility_50d_pct: float
    current_drawdown_pct: float
    max_drawdown_pct: float
    worst_daily_return_pct: float


class ScenarioItem(BaseModel):
    label: str
    move_pct: float
    dollar_impact: float


class OverviewResponse(BaseModel):
    symbol: str
    summary: OverviewSummary
    freshness: ForecastFreshness
    series: list[OverviewPoint]
    scenarios: list[ScenarioItem]


class ComparePoint(BaseModel):
    date: date
    symbol: str
    normalized_growth: float
    drawdown_pct: float


class CompareSummary(BaseModel):
    symbol: str
    cumulative_return_pct: float
    annualized_volatility_pct: float
    max_drawdown_pct: float
    current_drawdown_pct: float
    worst_daily_return_pct: float
    downside_days: int


class CompareResponse(BaseModel):
    start_date: date
    end_date: date
    available_start_date: date
    available_end_date: date
    latest_available_price_date: date
    points: list[ComparePoint]
    summaries: list[CompareSummary]


class EvidenceScore(BaseModel):
    symbol: str
    model: str
    mae: float
    mae_rows: int
    qlike: float | None
    qlike_rows: int


class EvidenceResponse(BaseModel):
    evaluation_start_date: date
    evaluation_end_date: date
    sample_size: int
    baseline_window: int
    realized_proxy: str
    qlike_note: str
    scores: list[EvidenceScore]


@lru_cache(maxsize=4)
def cached_forecast(symbol: str, horizon: int):
    """Reuse a forecast for stable local artifacts within one API process."""

    returns = load_returns(DATABASE_PATH)
    return create_five_day_forecast(returns, symbol=symbol, horizon=horizon)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service readiness."""

    return HealthResponse(status="ok", service="financial-risk-monitor")


@app.get("/symbols", response_model=list[SymbolResponse])
def symbols() -> list[SymbolResponse]:
    """List symbols configured for the monitor."""

    return [SymbolResponse(symbol=asset.symbol, name=asset.name, market=asset.market) for asset in ASSETS]


@app.get("/overview/{symbol}", response_model=OverviewResponse)
def overview(symbol: str, portfolio_value: float = 10000) -> OverviewResponse:
    """Return the selected-asset data contract needed by the Overview screen."""

    selected = symbol.upper()
    configured = {asset.symbol for asset in ASSETS}
    if selected not in configured:
        raise HTTPException(status_code=404, detail=f"Unsupported symbol: {selected}")
    if portfolio_value < 0:
        raise HTTPException(status_code=422, detail="Portfolio value cannot be negative")
    try:
        data = load_dashboard_data(selected, database_path=DATABASE_PATH)
        summary = summarize_asset(data)
        freshness = data.freshness
    except (FileNotFoundError, OSError) as error:
        raise HTTPException(status_code=503, detail="Overview data store is unavailable") from error
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=f"Overview data load failed: {error}") from error

    chart = data.prices[["date", "close"]].merge(
        data.rolling_volatility[["date", "volatility_20d"]], on="date", how="left"
    ).merge(data.returns[["date", "return_pct"]], on="date", how="left")
    chart = chart.iloc[:: max(1, len(chart) // 280)].tail(280)
    scenarios = calculate_scenarios(
        portfolio_value,
        latest_return_pct=float(data.returns.iloc[-1]["return_pct"]),
        worst_return_pct=summary.worst_daily_return_pct,
    )
    return OverviewResponse(
        symbol=selected,
        summary=OverviewSummary(**summary.__dict__),
        freshness=ForecastFreshness(
            latest_available_price_date=freshness.latest_available_price_date,
            model_training_cutoff=freshness.model_training_cutoff,
            forecast_generated_at_utc=freshness.forecast_generated_at_utc,
            forecast_start_date=freshness.forecast_start_date,
            forecast_end_date=freshness.forecast_end_date,
            forecast_status=freshness.forecast_status,
            is_current=freshness.is_current,
        ),
        series=[OverviewPoint(**row) for row in chart.where(chart.notna(), None).to_dict("records")],
        scenarios=[ScenarioItem(**item.__dict__) for item in scenarios],
    )


@app.get("/compare", response_model=CompareResponse)
def compare(start_date: date | None = None, end_date: date | None = None) -> CompareResponse:
    """Return aligned SPY/QQQ comparison data for the Compare view."""

    try:
        points, summaries = compare_assets(start_date=start_date, end_date=end_date, database_path=DATABASE_PATH)
    except (FileNotFoundError, OSError) as error:
        raise HTTPException(status_code=503, detail="Comparison data store is unavailable") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    available_prices = load_prices(DATABASE_PATH)
    return CompareResponse(
        start_date=points["date"].min().date(),
        end_date=points["date"].max().date(),
        available_start_date=available_prices["date"].min().date(),
        available_end_date=available_prices["date"].max().date(),
        latest_available_price_date=points["date"].max().date(),
        points=[
            ComparePoint(**row)
            for row in points[["date", "symbol", "normalized_growth", "drawdown_pct"]]
            .iloc[:: max(1, len(points) // 320)]
            .to_dict("records")
        ],
        summaries=[CompareSummary(**item.__dict__) for item in summaries],
    )


@app.get("/evidence", response_model=EvidenceResponse)
def evidence() -> EvidenceResponse:
    """Return stored out-of-sample model evidence and evaluation metadata."""

    try:
        evaluation = json.loads((METADATA_DIR / "rolling_evaluation_metadata.json").read_text(encoding="utf-8"))
        scores = json.loads((METADATA_DIR / "forecast_scores.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Model evidence artifacts are unavailable") from error
    return EvidenceResponse(
        evaluation_start_date=evaluation["test_start_date"],
        evaluation_end_date=evaluation["test_end_date"],
        sample_size=evaluation["target_rows"],
        baseline_window=evaluation["baseline_window"],
        realized_proxy=evaluation["realized_proxy"],
        qlike_note=scores["qlike_note"],
        scores=[EvidenceScore(**item) for item in scores["scores"]],
    )


@app.get("/evidence/diagnostics/acf-pacf")
def evidence_diagnostics() -> FileResponse:
    """Serve the generated squared-return ACF/PACF diagnostic image."""

    path = FIGURES_DIR / "squared_return_acf_pacf.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Diagnostics image is unavailable")
    return FileResponse(path, media_type="image/png")


@app.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest) -> ForecastResponse:
    """Return a baseline and GARCH forecast for the requested horizon."""

    symbol = request.symbol.upper()
    configured = {asset.symbol for asset in ASSETS}
    if symbol not in configured:
        raise HTTPException(status_code=404, detail=f"Unsupported symbol: {symbol}")
    try:
        rows = cached_forecast(symbol, request.horizon)
        freshness = load_freshness(database_path=DATABASE_PATH, symbol=symbol)
    except (FileNotFoundError, OSError) as error:
        raise HTTPException(status_code=503, detail="Forecast data store is unavailable") from error
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=f"Forecast calculation failed: {error}") from error
    if not rows:
        raise HTTPException(status_code=503, detail="No forecast rows were generated")
    items = [
        ForecastItem(
            forecast_date=row.forecast_date,
            horizon=row.horizon,
            model=row.model,
            variance_pct2=row.variance_pct2,
            volatility_pct=row.volatility_pct,
            training_end_date=row.training_end_date,
        )
        for row in rows
    ]
    return ForecastResponse(
        symbol=symbol,
        horizon=request.horizon,
        variance_units="percentage-points-squared",
        volatility_units="percentage points",
        forecasts=items,
        freshness=ForecastFreshness(
            latest_available_price_date=freshness.latest_available_price_date,
            model_training_cutoff=freshness.model_training_cutoff,
            forecast_generated_at_utc=freshness.forecast_generated_at_utc,
            forecast_start_date=items[0].forecast_date,
            forecast_end_date=items[-1].forecast_date,
            forecast_status=freshness.forecast_status,
            is_current=freshness.is_current,
        ),
    )
