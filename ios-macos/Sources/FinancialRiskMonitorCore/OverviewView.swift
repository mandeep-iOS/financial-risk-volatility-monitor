import Charts
import SwiftUI

public struct OverviewView: View {
    @ObservedObject private var model: AppModel
    @Binding private var selectedSymbol: String

    public init(model: AppModel, selectedSymbol: Binding<String>) {
        self.model = model
        _selectedSymbol = selectedSymbol
    }

    public var body: some View {
        Group {
            if model.overviewLoading { ProgressView("Loading \(selectedSymbol) overview…").tint(DashboardTheme.primary) }
            else if let error = model.overviewError { errorView(error) }
            else if let overview = model.overview { overviewContent(overview) }
            else { Text("Select an asset to begin.").foregroundStyle(DashboardTheme.muted) }
        }
        .task(id: selectedSymbol) { await model.loadOverview(symbol: selectedSymbol) }
    }

    private func overviewContent(_ overview: OverviewResponse) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                hero(overview)
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 145), spacing: 12)], spacing: 12) {
                    metric("5-day return", overview.summary.recent5dReturnPct, suffix: "%", risk: overview.summary.recent5dReturnPct < 0)
                    metric("20-day return", overview.summary.recent20dReturnPct, suffix: "%", risk: overview.summary.recent20dReturnPct < 0)
                    metric("20-day volatility", overview.summary.volatility20dPct, suffix: "%")
                    metric("50-day volatility", overview.summary.volatility50dPct, suffix: "%")
                    metric("Current drawdown", overview.summary.currentDrawdownPct, suffix: "%", risk: true)
                    metric("Max drawdown", overview.summary.maxDrawdownPct, suffix: "%", risk: true)
                }
                ViewThatFits(in: .horizontal) {
                    HStack(alignment: .top, spacing: 16) { chartCard(overview); insightCard(overview) }
                    VStack(spacing: 16) { chartCard(overview); insightCard(overview) }
                }
                ViewThatFits(in: .horizontal) {
                    HStack(alignment: .top, spacing: 16) { scenarioCard(overview); freshnessCard(overview) }
                    VStack(spacing: 16) { scenarioCard(overview); freshnessCard(overview) }
                }
            }.padding(24)
        }
    }

    private func hero(_ overview: OverviewResponse) -> some View {
        DashboardCard { HStack(alignment: .bottom) { VStack(alignment: .leading, spacing: 7) { Text("OVERVIEW / SELECTED ASSET").font(.caption.weight(.bold)).tracking(1.8).foregroundStyle(DashboardTheme.primary); Text("\(overview.symbol) risk profile").font(.title2.weight(.bold)); Text("Historical market behavior, realized volatility, and drawdown context.").font(.subheadline).foregroundStyle(DashboardTheme.muted) }; Spacer(); VStack(alignment: .trailing, spacing: 4) { Text("Latest close").font(.caption).foregroundStyle(DashboardTheme.muted); Text(overview.summary.latestClose, format: .currency(code: "USD")).font(.title.weight(.bold)); Text(date(overview.summary.latestPriceDate)).font(.caption).foregroundStyle(DashboardTheme.muted) } } }
    }

    private func metric(_ label: String, _ value: Double, suffix: String, risk: Bool = false) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 10) { Image(systemName: risk ? "chart.line.downtrend.xyaxis" : "waveform.path.ecg").foregroundStyle(risk ? DashboardTheme.risk : DashboardTheme.primary); Text(label).font(.caption).foregroundStyle(DashboardTheme.muted); Text("\(value >= 0 ? "+" : "")\(value, specifier: "%.1f")\(suffix)").font(.title3.weight(.bold)).foregroundStyle(risk ? DashboardTheme.risk : .white) } } }

    private func chartCard(_ overview: OverviewResponse) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 4) { Text("Price and volatility history").font(.headline.weight(.bold)); Text("\(overview.symbol) • close in USD • volatility annualized").font(.caption).foregroundStyle(DashboardTheme.muted); Chart { ForEach(overview.series) { point in LineMark(x: .value("Date", point.date), y: .value("Close", point.close)).foregroundStyle(DashboardTheme.primary).interpolationMethod(.catmullRom); if let volatility = point.volatility20d { LineMark(x: .value("Date", point.date), y: .value("Volatility", volatility)).foregroundStyle(DashboardTheme.risk).interpolationMethod(.catmullRom) } } }.chartXAxis(.hidden).chartYAxis { AxisMarks { AxisGridLine().foregroundStyle(DashboardTheme.border); AxisValueLabel().foregroundStyle(DashboardTheme.muted) } }.frame(minHeight: 260) } }.frame(maxWidth: .infinity)
    }

    private func insightCard(_ overview: OverviewResponse) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 12) { Label("Key insight", systemImage: "lightbulb.fill").font(.headline.weight(.bold)).foregroundStyle(DashboardTheme.primary); let comparison = overview.summary.volatility20dPct > overview.summary.volatility50dPct ? "above" : "below"; Text("\(overview.symbol) currently shows 20-day volatility \(comparison) its 50-day comparison window. The latest drawdown is \(overview.summary.currentDrawdownPct, specifier: "%.1f")% from the running peak.").font(.subheadline).foregroundStyle(.white).fixedSize(horizontal: false, vertical: true); Text("This is historical/example analysis through \(date(overview.freshness.latestAvailablePriceDate)) and is not investment advice.").font(.caption).foregroundStyle(DashboardTheme.muted) } }.frame(maxWidth: .infinity)
    }

    private func scenarioCard(_ overview: OverviewResponse) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 10) { Text("Portfolio move scenarios").font(.headline.weight(.bold)); Text("Illustration for a $10,000 holding • not a prediction").font(.caption).foregroundStyle(DashboardTheme.muted); ForEach(overview.scenarios) { scenario in HStack { Text(scenario.label).font(.caption).foregroundStyle(DashboardTheme.muted); Spacer(); Text(scenario.dollarImpact, format: .currency(code: "USD")).font(.subheadline.weight(.bold)).foregroundStyle(scenario.dollarImpact < 0 ? DashboardTheme.risk : DashboardTheme.positive) }.padding(10).background(DashboardTheme.panelRaised).clipShape(RoundedRectangle(cornerRadius: 8)) } } }.frame(maxWidth: .infinity)
    }

    private func freshnessCard(_ overview: OverviewResponse) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 10) { Label(overview.freshness.forecastStatus, systemImage: "clock.fill").foregroundStyle(overview.freshness.isCurrent ? DashboardTheme.positive : DashboardTheme.risk); Text("Prices through \(date(overview.freshness.latestAvailablePriceDate))").font(.caption).foregroundStyle(DashboardTheme.muted); Text("Model trained through \(date(overview.freshness.modelTrainingCutoff))").font(.caption).foregroundStyle(DashboardTheme.muted) } }.frame(maxWidth: .infinity)
    }

    private func errorView(_ message: String) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 8) { Text("Overview unavailable").font(.headline); Text(message).font(.caption).foregroundStyle(DashboardTheme.risk) } } }
    private func date(_ value: Date) -> String { value.formatted(date: .abbreviated, time: .omitted) }
}
