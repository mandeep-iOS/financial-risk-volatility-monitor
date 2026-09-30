export type SymbolInfo = {
  symbol: string
  name: string
  market: string
}

export type HealthResponse = {
  status: string
  service: string
}

export type Freshness = {
  latest_available_price_date: string
  model_training_cutoff: string
  forecast_generated_at_utc: string
  forecast_start_date: string
  forecast_end_date: string
  forecast_status: string
  is_current: boolean
}

export type ForecastResponse = {
  symbol: string
  horizon: number
  variance_units: string
  volatility_units: string
  forecasts: Array<Record<string, unknown>>
  freshness: Freshness
}

export type OverviewResponse = {
  symbol: string
  summary: {
    latest_close: number
    latest_price_date: string
    recent_5d_return_pct: number
    recent_20d_return_pct: number
    volatility_20d_pct: number
    volatility_50d_pct: number
    current_drawdown_pct: number
    max_drawdown_pct: number
    worst_daily_return_pct: number
  }
  freshness: Freshness
  series: Array<{ date: string; close: number; volatility_20d: number | null; return_pct: number | null }>
  scenarios: Array<{ label: string; move_pct: number; dollar_impact: number }>
}

export type CompareResponse = {
  start_date: string
  end_date: string
  latest_available_price_date: string
  points: Array<{ date: string; symbol: string; normalized_growth: number; drawdown_pct: number }>
  summaries: Array<{ symbol: string; cumulative_return_pct: number; annualized_volatility_pct: number; max_drawdown_pct: number; current_drawdown_pct: number; worst_daily_return_pct: number; downside_days: number }>
}

export type EvidenceResponse = {
  evaluation_start_date: string
  evaluation_end_date: string
  sample_size: number
  baseline_window: number
  realized_proxy: string
  qlike_note: string
  scores: Array<{ symbol: string; model: string; mae: number; mae_rows: number; qlike: number | null; qlike_rows: number }>
}
