import { useState, type ReactNode } from 'react'
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Activity, BarChart3, CalendarDays, FileText, Home, LineChart, Server, Shield, TrendingDown, TrendingUp, Waves } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from './api/client'
import type { SymbolInfo } from './api/types'

const navItems = [
  { label: 'Overview', path: '/overview', icon: Home },
  { label: 'Compare', path: '/compare', icon: LineChart },
  { label: 'Forecast', path: '/forecast', icon: BarChart3 },
  { label: 'Model Evidence', path: '/evidence', icon: FileText },
]

function AppShell() {
  const location = useLocation()
  const [selectedSymbol, setSelectedSymbol] = useState('SPY')
  const symbols = useQuery({ queryKey: ['symbols'], queryFn: api.symbols })
  const health = useQuery({ queryKey: ['health'], queryFn: api.health })
  const currentPage = navItems.find((item) => location.pathname.startsWith(item.path))?.label ?? 'Overview'

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true"><span /><span /><span /></div>
          <div><div className="brand-name">Financial Risk</div><div className="brand-name">Monitor</div></div>
        </div>
        <div className="sidebar-rule" />
        <nav className="side-nav" aria-label="Main navigation">
          {navItems.map(({ label, path, icon: Icon }) => (
            <NavLink className="nav-item" to={path} key={path}>
              <Icon size={19} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-caption"><Shield size={16} /> Educational analytics using historical market data.</div>
          <div className="sidebar-status"><span className={`status-dot ${health.isSuccess ? 'online' : ''}`} /> {health.isSuccess ? 'API connected' : 'Connecting to API'}</div>
        </div>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <div>
            <div className="eyebrow">Financial risk analytics</div>
            <h1>{currentPage === 'Overview' ? 'Financial Risk Monitor' : currentPage}</h1>
            <p>Analyze market risk and volatility using historical data and statistical models.</p>
          </div>
          <div className="header-controls">
            <label className="field-label" htmlFor="asset">Asset</label>
            <select id="asset" value={selectedSymbol} onChange={(event) => setSelectedSymbol(event.target.value)}>
              {(symbols.data ?? [{ symbol: 'SPY', name: 'S&P 500 ETF', market: 'US' }]).map((symbol: SymbolInfo) => (
                <option key={symbol.symbol} value={symbol.symbol}>{symbol.symbol}</option>
              ))}
            </select>
            <div className="status-pill"><Server size={15} /> Historical demo</div>
          </div>
        </header>
        <div className="freshness-row"><Activity size={15} /> Prices and models use the latest available project artifacts <span>•</span> Selected asset: <strong>{selectedSymbol}</strong></div>
        <Routes>
          <Route path="/" element={<Navigate to="/overview" replace />} />
          <Route path="/overview" element={<OverviewPage symbol={selectedSymbol} />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/forecast" element={<ForecastPage symbol={selectedSymbol} />} />
          <Route path="/evidence" element={<EvidencePage />} />
        </Routes>
      </main>
    </div>
  )
}

function OverviewPage({ symbol }: { symbol: string }) {
  const overview = useQuery({ queryKey: ['overview', symbol], queryFn: () => api.overview(symbol) })
  if (overview.isLoading) return <section className="loading-panel">Loading selected asset…</section>
  if (overview.isError || !overview.data) return <section className="error-panel">Overview data could not be loaded. Confirm that FastAPI is running on port 8000.</section>
  const { summary, freshness, scenarios, series } = overview.data
  const volatilityDirection = summary.volatility_20d_pct > summary.volatility_50d_pct ? 'above' : 'below'
  return <>
    <section className="overview-hero">
      <div><div className="section-kicker">Overview / selected asset</div><h2>{symbol} risk profile</h2><p>Historical market behavior, realized volatility, and drawdown context for the selected asset.</p></div>
      <div className="hero-stat"><span>Latest close</span><strong>${summary.latest_close.toFixed(2)}</strong><small>through {formatDate(summary.latest_price_date)}</small></div>
    </section>
    <div className="kpi-grid">
      <Kpi icon={<TrendingUp />} label="5-day return" value={formatPct(summary.recent_5d_return_pct)} tone={summary.recent_5d_return_pct >= 0 ? 'positive' : 'risk'} />
      <Kpi icon={<TrendingUp />} label="20-day return" value={formatPct(summary.recent_20d_return_pct)} tone={summary.recent_20d_return_pct >= 0 ? 'positive' : 'risk'} />
      <Kpi icon={<Waves />} label="20-day volatility" value={formatPct(summary.volatility_20d_pct)} tone="blue" />
      <Kpi icon={<Waves />} label="50-day volatility" value={formatPct(summary.volatility_50d_pct)} tone="blue" />
      <Kpi icon={<TrendingDown />} label="Current drawdown" value={formatPct(summary.current_drawdown_pct)} tone="risk" />
      <Kpi icon={<TrendingDown />} label="Max drawdown" value={formatPct(summary.max_drawdown_pct)} tone="risk" />
    </div>
    <div className="chart-grid">
      <ChartPanel title="Price and volatility history" subtitle={`${symbol} • ${formatDate(series[0]?.date)} to ${formatDate(series.at(-1)?.date)} • close in USD, volatility annualized`}>
        <MarketChart series={series} />
      </ChartPanel>
      <section className="insight-panel"><div className="panel-heading"><div className="icon-bubble blue"><Activity size={19} /></div><div><div className="panel-title">Key insight</div><div className="panel-subtitle">Plain-English risk context</div></div></div><p>{symbol} currently shows 20-day volatility <strong>{volatilityDirection}</strong> its 50-day comparison window. The latest drawdown is <strong>{formatPct(summary.current_drawdown_pct)}</strong> from the running peak.</p><p className="muted">This is historical/example analysis through {formatDate(freshness.latest_available_price_date)} and is not investment advice.</p></section>
    </div>
    <div className="bottom-grid"><ScenarioPanel scenarios={scenarios} /><section className="freshness-card"><div className="panel-title">Data status</div><div className="freshness-item"><span>Prices through</span><strong>{formatDate(freshness.latest_available_price_date)}</strong></div><div className="freshness-item"><span>Model trained through</span><strong>{formatDate(freshness.model_training_cutoff)}</strong></div><div className="freshness-item"><span>Forecast status</span><strong className="risk-text">{freshness.forecast_status}</strong></div></section></div>
  </>
}

function ComparePage() {
  const [startDate, setStartDate] = useState('2016-09-28')
  const [endDate, setEndDate] = useState('2025-12-31')
  const comparison = useQuery({ queryKey: ['compare', startDate, endDate], queryFn: () => api.compare(startDate, endDate) })
  if (comparison.isLoading) return <section className="loading-panel">Loading comparison…</section>
  if (comparison.isError || !comparison.data) return <section className="error-panel">Comparison data could not be loaded.</section>
  const { points, summaries } = comparison.data
  const spy = summaries.find((item) => item.symbol === 'SPY')!
  const qqq = summaries.find((item) => item.symbol === 'QQQ')!
  return <>
    <section className="page-heading"><div><div className="section-kicker">Compare assets</div><h2>Which asset carried more risk?</h2><p>Compare growth, volatility, and drawdown using the selected historical window.</p></div><div className="date-controls"><label>From<input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label><label>To<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label></div></section>
    <div className="compare-kpis"><CompareKpi title="Cumulative return" a={spy.cumulative_return_pct} b={qqq.cumulative_return_pct} suffix="%" /><CompareKpi title="Annualized volatility" a={spy.annualized_volatility_pct} b={qqq.annualized_volatility_pct} suffix="%" /><CompareKpi title="Max drawdown" a={spy.max_drawdown_pct} b={qqq.max_drawdown_pct} suffix="%" /><CompareKpi title="Downside days" a={spy.downside_days} b={qqq.downside_days} suffix=" days" /></div>
    <div className="compare-chart-grid"><ChartPanel title="Normalized growth" subtitle={`Both assets start at 100 • ${formatDate(comparison.data.start_date)} to ${formatDate(comparison.data.end_date)}`}><CompareChart points={points} field="normalized_growth" /></ChartPanel><div className="stacked-charts"><ChartPanel title="Drawdown from peak" subtitle="More negative means a larger decline"><CompareChart points={points} field="drawdown_pct" /></ChartPanel><ChartPanel title="Risk readout" subtitle="Historical comparison, not investment advice"><p className="comparison-copy">{spy.cumulative_return_pct > qqq.cumulative_return_pct ? 'SPY' : 'QQQ'} delivered the higher cumulative return. {spy.annualized_volatility_pct > qqq.annualized_volatility_pct ? 'SPY' : 'QQQ'} carried higher annualized volatility, while {spy.max_drawdown_pct < qqq.max_drawdown_pct ? 'SPY' : 'QQQ'} experienced the deeper maximum drawdown.</p></ChartPanel></div></div>
  </>
}

function ForecastPage({ symbol }: { symbol: string }) { const forecast = useQuery({ queryKey: ['forecast', symbol], queryFn: () => api.forecast(symbol) }); if (forecast.isLoading) return <section className="loading-panel">Loading forecast…</section>; if (forecast.isError || !forecast.data) return <section className="error-panel">Forecast data could not be loaded.</section>; const data = forecast.data; const values = data.forecasts.map((item) => ({ date: String(item.forecast_date), value: Number(item.volatility_pct) })); return <><section className="page-heading"><div><div className="section-kicker">Forecast / selected asset</div><h2>Volatility forecast</h2><p>Near-term model estimates for {symbol}, with freshness shown explicitly.</p></div><div className="status-pill"><CalendarDays size={15} /> {data.freshness.forecast_status}</div></section><div className="forecast-meta"><span>Model trained through <strong>{formatDate(data.freshness.model_training_cutoff)}</strong></span><span>Generated <strong>{new Date(data.freshness.forecast_generated_at_utc).toLocaleString()}</strong></span><span>Forecast window <strong>{formatDate(data.freshness.forecast_start_date)} – {formatDate(data.freshness.forecast_end_date)}</strong></span></div><div className="forecast-grid"><ChartPanel title={`Forecasted volatility • ${symbol}`} subtitle="Daily volatility in percentage points • baseline and GARCH estimates"><ForecastChart values={values} /></ChartPanel><section className="insight-panel"><div className="panel-title">What this means</div><p>The model estimates near-term volatility for the next {data.horizon} trading sessions. These are historical/example estimates because the available price data is not current.</p><p className="muted">Forecasts are probabilistic and educational, not investment advice.</p></section></div><section className="forecast-table-panel"><div className="panel-title">Technical forecast details</div><div className="forecast-table">{data.forecasts.map((item) => <div className="forecast-row" key={`${item.model}-${item.forecast_date}`}><span>{String(item.forecast_date)}</span><strong>{String(item.model)}</strong><span>{Number(item.volatility_pct).toFixed(2)} pp volatility</span></div>)}</div></section></> }

function EvidencePage() { const evidence = useQuery({ queryKey: ['evidence'], queryFn: api.evidence }); if (evidence.isLoading) return <section className="loading-panel">Loading model evidence…</section>; if (evidence.isError || !evidence.data) return <section className="error-panel">Model evidence artifacts could not be loaded.</section>; const data = evidence.data; const bySymbol = ['SPY', 'QQQ'].map((symbol) => { const rows = data.scores.filter((score) => score.symbol === symbol); const baseline = rows.find((row) => row.model === 'baseline')!; const garch = rows.find((row) => row.model === 'garch')!; return { symbol, baseline, garch, maeWinner: garch.mae < baseline.mae ? 'GARCH' : 'Baseline', qlikeWinner: (garch.qlike ?? Infinity) < (baseline.qlike ?? Infinity) ? 'GARCH' : 'Baseline' } }); return <><section className="page-heading"><div><div className="section-kicker">Model evidence</div><h2>Why should I trust this?</h2><p>Out-of-sample comparison of a rolling baseline and GARCH volatility forecasts.</p></div><div className="status-pill"><Activity size={15} /> Evidence, not certainty</div></section><div className="evidence-meta"><span>Evaluation window <strong>{formatDate(data.evaluation_start_date)} – {formatDate(data.evaluation_end_date)}</strong></span><span>Sample size <strong>{data.sample_size} targets</strong></span><span>Baseline window <strong>{data.baseline_window} sessions</strong></span></div><section className="explain-grid"><div className="explain-card"><strong>MAE</strong><p>Mean absolute error: the average size of the forecast miss. Lower is better.</p></div><div className="explain-card"><strong>QLIKE</strong><p>A variance-forecast loss function that penalizes poor scale estimates. Lower is better.</p></div></section><div className="winner-grid">{bySymbol.map((item) => <section className="winner-card" key={item.symbol}><div className="winner-header"><div><div className="section-kicker">{item.symbol}</div><div className="panel-title">Model comparison</div></div><span className="winner-pill">{item.maeWinner} leads</span></div><div className="score-line"><span>MAE</span><strong>Baseline {item.baseline.mae.toFixed(3)}</strong><strong className="garch-text">GARCH {item.garch.mae.toFixed(3)}</strong></div><div className="score-line"><span>QLIKE</span><strong>Baseline {(item.baseline.qlike ?? 0).toFixed(3)}</strong><strong className="garch-text">GARCH {(item.garch.qlike ?? 0).toFixed(3)}</strong></div><div className="winner-foot">MAE winner: <b>{item.maeWinner}</b> • QLIKE winner: <b>{item.qlikeWinner}</b> • {item.baseline.mae_rows} rows</div></section>)}</div><details className="diagnostics-panel"><summary>Technical diagnostics: ACF/PACF and scoring notes</summary><p>Squared-return dependence diagnostics are kept here for technical readers. QLIKE excludes rows with zero or non-positive realized variance.</p><img src="http://127.0.0.1:8000/evidence/diagnostics/acf-pacf" alt="Squared-return ACF and PACF diagnostics" /></details></> }

function CompareKpi({ title, a, b, suffix }: { title: string; a: number; b: number; suffix: string }) { return <div className="compare-kpi"><span>{title}</span><div><strong className="spy-text">SPY {a >= 0 ? '+' : ''}{a.toFixed(1)}{suffix}</strong><strong className="qqq-text">QQQ {b >= 0 ? '+' : ''}{b.toFixed(1)}{suffix}</strong></div></div> }
function CompareChart({ points, field }: { points: Array<{ symbol: string; [key: string]: string | number }>; field: string }) { const lines = ['SPY', 'QQQ'].map((symbol) => points.filter((point) => point.symbol === symbol)); const all = lines.flat().map((point) => Number(point[field])); const min = Math.min(...all); const max = Math.max(...all); return <div className="mini-chart"><svg viewBox="0 0 100 100" preserveAspectRatio="none">{lines.map((line, index) => <path key={index} className={index === 0 ? 'spy-line' : 'qqq-line'} d={line.map((point, i) => `${i ? 'L' : 'M'} ${(i / Math.max(line.length - 1, 1)) * 100} ${100 - ((Number(point[field]) - min) / Math.max(max - min, 1)) * 82 - 8}`).join(' ')} />)}</svg><div className="chart-legend"><span className="legend-orange">━ SPY</span><span className="legend-blue">━ QQQ</span></div></div> }
function ForecastChart({ values }: { values: Array<{ date: string; value: number }> }) { const max = Math.max(...values.map((item) => item.value)); const min = Math.min(...values.map((item) => item.value)); return <div className="mini-chart forecast-chart"><svg viewBox="0 0 100 100" preserveAspectRatio="none"><path className="forecast-line" d={values.map((item, i) => `${i ? 'L' : 'M'} ${(i / Math.max(values.length - 1, 1)) * 100} ${100 - ((item.value - min) / Math.max(max - min, 1)) * 82 - 8}`).join(' ')} /></svg><div className="chart-legend"><span className="legend-orange">━ Model volatility</span></div></div> }

function Kpi({ icon, label, value, tone }: { icon: ReactNode; label: string; value: string; tone: string }) { return <div className={`kpi-card ${tone}`}><div className="kpi-icon">{icon}</div><span>{label}</span><strong>{value}</strong></div> }
function ChartPanel({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) { return <section className="chart-panel"><div className="panel-title">{title}</div><div className="panel-subtitle">{subtitle}</div>{children}</section> }
function ScenarioPanel({ scenarios }: { scenarios: Array<{ label: string; move_pct: number; dollar_impact: number }> }) { return <section className="scenario-panel"><div className="panel-title">Portfolio move scenarios</div><div className="panel-subtitle">Illustration for a $10,000 holding • not a prediction</div><div className="scenario-grid">{scenarios.map((scenario) => <div className="scenario-row" key={scenario.label}><span>{scenario.label}</span><strong className={scenario.dollar_impact < 0 ? 'risk-text' : 'positive-text'}>{formatDollar(scenario.dollar_impact)}</strong></div>)}</div></section> }
function MarketChart({ series }: { series: Array<{ date: string; close: number; volatility_20d: number | null }> }) { const points = series.filter((point) => point.close && point.volatility_20d); const maxClose = Math.max(...points.map((p) => p.close)); const minClose = Math.min(...points.map((p) => p.close)); const maxVol = Math.max(...points.map((p) => p.volatility_20d ?? 0)); const path = (key: 'close' | 'volatility_20d', max: number, min = 0) => points.map((point, index) => `${index ? 'L' : 'M'} ${(index / Math.max(points.length - 1, 1)) * 100} ${100 - (((point[key] ?? 0) - min) / Math.max(max - min, 1)) * 82 - 8}`).join(' '); return <div className="market-chart"><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Price and volatility history chart"><defs><linearGradient id="priceFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#4ba4ff" stopOpacity=".22" /><stop offset="1" stopColor="#4ba4ff" stopOpacity="0" /></linearGradient></defs><path d={`${path('close', maxClose, minClose)} L 100 100 L 0 100 Z`} fill="url(#priceFill)" /><path d={path('close', maxClose, minClose)} className="price-line" /><path d={path('volatility_20d', maxVol)} className="vol-line" /></svg><div className="chart-legend"><span className="legend-blue">━ Close price</span><span className="legend-orange">━ 20-day volatility</span></div></div> }
function formatPct(value: number) { return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%` }
function formatDollar(value: number) { return `${value >= 0 ? '+' : '-'}$${Math.abs(value).toFixed(0)}` }
function formatDate(value?: string) { return value ? new Date(`${value}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—' }

function EmptyPage({ title, symbol }: { title: string; symbol: string }) {
  return <section className="placeholder-panel"><div className="section-kicker">Phase 1 shell</div><h2>{title}</h2><p>{title} is connected to the shared dashboard shell and ready for the next implementation phase.</p><div className="placeholder-chip">Selected asset: <strong>{symbol}</strong></div></section>
}

export default function App() { return <AppShell /> }
