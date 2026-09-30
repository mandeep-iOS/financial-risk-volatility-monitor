"""User-facing Streamlit shell for the financial risk monitor."""

from __future__ import annotations

from datetime import UTC, datetime

import altair as alt
import pandas as pd
import streamlit as st

from risk_monitor.dashboard_data import (
    calculate_scenarios,
    compare_assets,
    load_backtest_forecasts,
    load_dashboard_data,
    load_scores,
    summarize_asset,
)

st.set_page_config(page_title="Financial Risk Monitor", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    :root { --ink: #f4f7fb; --muted: #a9b9ce; --line: #2a405d; --panel: #111f33; --accent: #3e9cff; --orange: #ff8a3d; }
    .stApp { background: #081321; color: var(--ink); }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #081321 0%, #0b1a2c 58%, #0d2035 100%); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #0b1a2d; border-right: 1px solid #1e3551; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
    .block-container { max-width: 1240px; padding-top: 2.2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    h1 { font-size: 2.55rem !important; line-height: 1.05; }
    h2 { margin-top: 1.8rem; }
    [data-testid="stMetric"] { background: rgba(17, 31, 51, 0.92); border: 1px solid var(--line); border-radius: 10px; padding: 0.95rem 1rem; min-height: 106px; box-shadow: 0 8px 24px rgba(0,0,0,.12); }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: #f7fbff; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    [data-testid="stVerticalBlockBorderWrapper"] { background: rgba(17, 31, 51, .65); border-color: var(--line); border-radius: 12px; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] .stRadio > label { color: #8fa7c1; font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; }
    [data-testid="stSidebar"] .stRadio label { background: transparent; border-radius: 8px; padding: .55rem .7rem; color: #c9d8eb; }
    [data-testid="stSidebar"] .stRadio label:hover { background: #193354; }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) { background: linear-gradient(90deg, #244b7c, #1b3558); color: #ffffff; box-shadow: inset 3px 0 #4ba4ff; }
    div[data-baseweb="select"] > div { background: #10243d; border-color: #315172; }
    button[kind="secondary"] { border-color: #315172; color: #dbeafe; }
    .brand { padding: .5rem .25rem 1.4rem; border-bottom: 1px solid #29405c; margin-bottom: 1.2rem; }
    .brand-mark { color: var(--accent); font-size: 1.8rem; font-weight: 800; letter-spacing: .08em; }
    .brand-name { color: #f6f9fd; font-size: 1.16rem; font-weight: 750; line-height: 1.15; }
    .brand-sub { color: var(--muted); font-size: .76rem; margin-top: .35rem; }
    .hero-kicker { color: var(--accent); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .hero-copy { color: var(--muted); font-size: 1rem; margin-top: -.45rem; margin-bottom: 1.2rem; }
    .section-kicker { color: var(--accent); font-size: .75rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
    .status-pill { display: inline-block; padding: .35rem .7rem; border: 1px solid #315172; border-radius: 999px; color: #dbeafe; background: #10243d; font-size: .78rem; }
    .hero-row { display: flex; justify-content: space-between; align-items: end; gap: 1rem; margin-bottom: .6rem; }
    .hero-status { color: #b9c9dd; font-size: .78rem; padding: .45rem .75rem; border: 1px solid #315172; border-radius: 999px; background: #10243d; white-space: nowrap; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; margin: 1rem 0 1.1rem; }
    .kpi-card { background: linear-gradient(145deg, #12243b, #0f1d30); border: 1px solid #2b4665; border-radius: 11px; padding: 1rem; min-height: 105px; box-shadow: 0 9px 22px rgba(0,0,0,.16); }
    .kpi-label { color: #a8bad0; font-size: .78rem; }
    .kpi-value { color: #f7fbff; font-size: 1.7rem; font-weight: 750; margin-top: .55rem; }
    .kpi-meta { color: #6faeff; font-size: .72rem; margin-top: .25rem; }
    .panel-title { color: #f4f7fb; font-size: 1.12rem; font-weight: 700; }
    .panel-subtitle { color: #91a7c0; font-size: .78rem; margin-bottom: .75rem; }
    @media (max-width: 760px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .hero-row { display: block; } .hero-status { display: inline-block; margin-top: .6rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def dark_chart(frame: pd.DataFrame, *, x: str, y: str, color: str | None = None, title: str = ""):
    chart = alt.Chart(frame).mark_line(strokeWidth=2).encode(
        x=alt.X(f"{x}:T", axis=alt.Axis(labelColor="#9fb3c9", titleColor="#9fb3c9", gridColor="#233a55")),
        y=alt.Y(f"{y}:Q", axis=alt.Axis(labelColor="#9fb3c9", titleColor="#9fb3c9", gridColor="#233a55")),
        tooltip=[x, y] + ([color] if color else []),
    )
    if color:
        chart = chart.encode(color=alt.Color(f"{color}:N", scale=alt.Scale(range=["#4ba4ff", "#ff8a3d"]), legend=alt.Legend(labelColor="#d7e5f4", titleColor="#d7e5f4")))
    return chart.properties(title=alt.TitleParams(title, color="#edf4fb", fontSize=14), background="#111f33", height=280).configure_view(stroke="#2b4665").configure_axis(domainColor="#52708f")


def panel_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="panel-title">{title}</div><div class="panel-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def kpi_grid(cards: list[tuple[str, str, str]]) -> None:
    html = '<div class="kpi-grid">' + "".join(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-meta">{meta}</div></div>'
        for label, value, meta in cards
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def pct(value: float | None) -> str:
    return "Unavailable" if value is None or pd.isna(value) else f"{value:.2f}%"


def render_freshness(data) -> None:
    freshness = data.freshness
    st.caption(
        f"Prices through: {freshness.latest_available_price_date:%Y-%m-%d}  |  "
        f"Model trained through: {freshness.model_training_cutoff:%Y-%m-%d}  |  "
        f"Forecast status: {freshness.forecast_status}"
    )


def render_overview(data) -> None:
    st.markdown('<div class="section-kicker">Overview</div>', unsafe_allow_html=True)
    st.subheader(f"What is happening with {data.selected_symbol}?")
    summary = summarize_asset(data)
    kpi_grid([
        ("Latest close", f"${summary.latest_close:.2f}", f"Through {summary.latest_price_date:%Y-%m-%d}"),
        ("5-day return", pct(summary.recent_5d_return_pct), "Close-to-close"),
        ("20-day return", pct(summary.recent_20d_return_pct), "Close-to-close"),
        ("Current drawdown", pct(summary.current_drawdown_pct), "From running peak"),
        ("20-day volatility", pct(summary.volatility_20d_pct), "Annualized"),
        ("50-day volatility", pct(summary.volatility_50d_pct), "Annualized"),
        ("Max drawdown", pct(summary.max_drawdown_pct), "Selected period"),
        ("Latest date", f"{summary.latest_price_date:%Y-%m-%d}", "Latest available"),
    ])
    risk_level = "higher" if summary.volatility_20d_pct > summary.volatility_50d_pct else "lower"
    drawdown_text = (
        f"It is currently {abs(summary.current_drawdown_pct):.2f}% below its running peak."
        if summary.current_drawdown_pct < 0
        else "It is currently at its running peak."
    )
    freshness_text = (
        "The displayed values are historical/example results because the data does not reach today."
        if data.freshness.forecast_status == "historical/example"
        else "The displayed values use the latest available dataset."
    )
    st.info(
        f"{data.selected_symbol} short-term volatility is {risk_level} than its 50-day comparison window. "
        f"{drawdown_text} {freshness_text} This is descriptive context, not a prediction."
    )
    with st.container(border=True):
        panel_header("Price history", f"{data.selected_symbol} daily close through {data.freshness.latest_available_price_date:%Y-%m-%d}; unit: USD")
        st.altair_chart(dark_chart(data.prices, x="date", y="close", title=f"{data.selected_symbol} close price"), width="stretch")
    with st.container(border=True):
        panel_header("Daily returns", f"{data.selected_symbol} close-to-close returns, {data.returns['date'].min():%Y-%m-%d} to {data.returns['date'].max():%Y-%m-%d}; unit: percent")
        st.altair_chart(dark_chart(data.returns, x="date", y="return_pct", title=f"{data.selected_symbol} daily returns"), width="stretch")
    st.subheader("Dollar move scenarios")
    st.caption("Scenario analysis only. These figures are arithmetic illustrations, not predictions.")
    portfolio_value = st.number_input("Portfolio value ($)", min_value=0.0, value=10000.0, step=1000.0)
    scenarios = calculate_scenarios(
        portfolio_value,
        latest_return_pct=float(data.returns.iloc[-1]["return_pct"]),
        worst_return_pct=summary.worst_daily_return_pct,
    )
    scenario_frame = pd.DataFrame(
        [{"Scenario": row.label, "Move (%)": row.move_pct, "Dollar impact ($)": row.dollar_impact} for row in scenarios]
    )
    st.dataframe(scenario_frame.style.format({"Move (%)": "{:.2f}", "Dollar impact ($)": "${:,.2f}"}), hide_index=True, width="stretch")


def render_compare() -> None:
    st.markdown('<div class="section-kicker">Cross-asset view</div>', unsafe_allow_html=True)
    st.subheader("Which asset carried more risk?")
    full_prices, _ = compare_assets()
    min_date = full_prices["date"].min().date()
    max_date = full_prices["date"].max().date()
    default_range = st.session_state.get("compare_date_range", (min_date, max_date))
    selected_range = st.date_input("Comparison date range", value=default_range, min_value=min_date, max_value=max_date)
    if len(selected_range) != 2:
        st.warning("Choose both a start and end date to compare the assets.")
        return
    start_date, end_date = selected_range
    st.session_state["compare_date_range"] = (start_date, end_date)
    chart_data, summaries = compare_assets(start_date=start_date, end_date=end_date)
    summary_frame = pd.DataFrame([summary.__dict__ for summary in summaries]).set_index("symbol")
    summary_frame = summary_frame.rename(columns={
        "cumulative_return_pct": "Cumulative return (%)",
        "annualized_volatility_pct": "Annualized volatility (%)",
        "max_drawdown_pct": "Max drawdown (%)",
        "current_drawdown_pct": "Current drawdown (%)",
        "worst_daily_return_pct": "Worst daily return (%)",
        "downside_days": "Downside days",
    })
    kpi_grid([
        ("SPY cumulative return", f"{summary_frame.loc['SPY', 'Cumulative return (%)']:.2f}%", "Selected range"),
        ("QQQ cumulative return", f"{summary_frame.loc['QQQ', 'Cumulative return (%)']:.2f}%", "Selected range"),
        ("SPY volatility", f"{summary_frame.loc['SPY', 'Annualized volatility (%)']:.2f}%", "Annualized"),
        ("QQQ volatility", f"{summary_frame.loc['QQQ', 'Annualized volatility (%)']:.2f}%", "Annualized"),
    ])
    st.caption(f"Normalized growth starts each asset at 100 on {start_date:%Y-%m-%d}.")
    with st.container(border=True):
        panel_header("Normalized growth", f"Both assets indexed to 100 on {start_date:%Y-%m-%d}; unit: index points")
        st.altair_chart(dark_chart(chart_data, x="date", y="normalized_growth", color="symbol", title="SPY vs QQQ normalized growth"), width="stretch")
    st.caption(f"Normalized growth for SPY and QQQ; unit: index points; date range: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}.")
    volatility = chart_data.copy()
    volatility["volatility_20d"] = volatility.groupby("symbol")["normalized_growth"].transform(lambda series: series.pct_change().rolling(20).std() * 252**0.5 * 100)
    vol_long = volatility[["date", "symbol", "volatility_20d"]].rename(columns={"volatility_20d": "value"})
    with st.container(border=True):
        panel_header("Rolling volatility", f"20-session annualized volatility; unit: percent; range: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
        st.altair_chart(dark_chart(vol_long, x="date", y="value", color="symbol", title="20-day rolling volatility"), width="stretch")
    st.caption(f"20-session rolling annualized volatility; unit: percent; date range: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}.")
    dd_long = chart_data[["date", "symbol", "drawdown_pct"]].rename(columns={"drawdown_pct": "value"})
    with st.container(border=True):
        panel_header("Drawdown", f"From each selected-period running peak; unit: percent; range: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
        st.altair_chart(dark_chart(dd_long, x="date", y="value", color="symbol", title="Drawdown from peak"), width="stretch")
    st.caption(f"Drawdown from each selected-period running peak; unit: percent; date range: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}.")
    highest_return = max(summaries, key=lambda summary: summary.cumulative_return_pct).symbol
    highest_vol = max(summaries, key=lambda summary: summary.annualized_volatility_pct).symbol
    worst_drawdown = min(summaries, key=lambda summary: summary.max_drawdown_pct).symbol
    st.info(
        f"From {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}, {highest_return} had the higher cumulative return, "
        f"{highest_vol} had the higher annualized volatility, and {worst_drawdown} had the deeper maximum drawdown. "
        "These are historical comparisons, not investment recommendations."
    )


def render_forecast(data) -> None:
    st.markdown('<div class="section-kicker">Forward view</div>', unsafe_allow_html=True)
    freshness = data.freshness
    st.subheader(f"What does the model estimate next for {data.selected_symbol}?")
    st.caption(
        f"Model trained through: {freshness.model_training_cutoff:%Y-%m-%d} | "
        f"Forecast generated: {freshness.forecast_generated_at_utc:%Y-%m-%d %H:%M UTC} | "
        f"Forecast dates: {freshness.forecast_start_date:%Y-%m-%d} to {freshness.forecast_end_date:%Y-%m-%d}"
    )
    if not freshness.is_current:
        st.warning("This is a historical/example forecast because the price data does not reach today.")
    with st.container(border=True):
        panel_header("Volatility forecast", f"{data.selected_symbol} five-session forecast; unit: percent; range: {freshness.forecast_start_date:%Y-%m-%d} to {freshness.forecast_end_date:%Y-%m-%d}")
        st.altair_chart(dark_chart(data.forecasts, x="forecast_date", y="volatility_pct", color="model", title=f"{data.selected_symbol} forecast volatility"), width="stretch")
    st.caption(f"{data.selected_symbol} five-session volatility forecast; unit: percent; date range: {freshness.forecast_start_date:%Y-%m-%d} to {freshness.forecast_end_date:%Y-%m-%d}.")
    latest_baseline = data.forecasts[data.forecasts["model"] == "baseline"].iloc[0]["volatility_pct"]
    latest_garch = data.forecasts[data.forecasts["model"] == "garch"].iloc[0]["volatility_pct"]
    direction = "higher" if latest_garch > latest_baseline else "lower"
    st.info(
        f"For the first forecast session, GARCH estimates {latest_garch:.2f}% volatility versus "
        f"{latest_baseline:.2f}% for the historical baseline. Across this example horizon, "
        f"the GARCH estimate is {direction} than the baseline; this is a model output, not a prediction of price direction."
    )
    with st.expander("Technical variance table"):
        st.dataframe(data.forecasts, hide_index=True)


def render_evidence(data) -> None:
    st.markdown('<div class="section-kicker">Model evidence</div>', unsafe_allow_html=True)
    st.subheader("Why should I trust this?")
    backtest = load_backtest_forecasts(symbol=data.selected_symbol)
    all_scores = load_scores()
    st.caption(
        f"Backtest dates: {backtest['target_date'].min():%Y-%m-%d} to "
        f"{backtest['target_date'].max():%Y-%m-%d} | "
        f"{len(backtest)} aligned observations for {data.selected_symbol}"
    )
    st.write(
        "The backtest compares both models on the same chronological targets. MAE measures "
        "average absolute variance error. QLIKE is a positive-variance scoring rule; its sample "
        "excludes zero realized-variance proxy rows. Lower values are better within this sample."
    )
    score_chart = all_scores[all_scores["symbol"].isin(["SPY", "QQQ"])].pivot(index="symbol", columns="model", values="mae")
    st.bar_chart(score_chart, y_label="MAE (percentage-points-squared)")
    st.caption("Backtest MAE by asset and model; lower is better.")
    qlike_chart = all_scores[all_scores["symbol"].isin(["SPY", "QQQ"])].pivot(index="symbol", columns="model", values="qlike")
    st.bar_chart(qlike_chart, y_label="QLIKE")
    st.caption("Backtest QLIKE by asset and model; lower is better.")
    selected_scores = data.scores[data.scores["symbol"] == data.selected_symbol]
    better_mae = selected_scores.loc[selected_scores["mae"].idxmin(), "model"]
    better_qlike = selected_scores.loc[selected_scores["qlike"].idxmin(), "model"]
    st.info(
        f"For {data.selected_symbol}, {better_mae.upper()} has the lower MAE and "
        f"{better_qlike.upper()} has the lower QLIKE in this backtest sample. "
        "That does not establish accuracy outside this period."
    )
    with st.expander("Selected-symbol score details"):
        st.dataframe(selected_scores, hide_index=True, width="stretch")
    with st.expander("Technical diagnostics: squared-return ACF/PACF"):
        st.image("docs/figures/squared_return_acf_pacf.png", caption="Squared-return dependence diagnostics")


st.sidebar.markdown(
    '<div class="brand"><div class="brand-mark">▮▮▮</div><div class="brand-name">Financial Risk<br>Monitor</div><div class="brand-sub">Market risk and volatility analytics</div></div>',
    unsafe_allow_html=True,
)
st.sidebar.caption("Educational analysis using historical daily data")
symbol = st.sidebar.selectbox("Selected asset", ["SPY", "QQQ"])
section = st.sidebar.radio("View", ["Overview", "Compare", "Forecast", "Model Evidence"])
try:
    data = load_dashboard_data(symbol, as_of=datetime.now(UTC).date())
except (FileNotFoundError, OSError, ValueError) as error:
    st.error(f"The selected asset data is unavailable: {error}")
    st.stop()
st.markdown('<div class="hero-kicker">Financial risk analytics</div>', unsafe_allow_html=True)
st.title("Financial Risk & Volatility Monitor")
st.markdown(
    '<div class="hero-copy">A practical view of price behavior, realized risk, and statistical volatility forecasts.</div>',
    unsafe_allow_html=True,
)
render_freshness(data)

if section == "Overview":
    render_overview(data)
elif section == "Compare":
    render_compare()
elif section == "Forecast":
    render_forecast(data)
else:
    render_evidence(data)
