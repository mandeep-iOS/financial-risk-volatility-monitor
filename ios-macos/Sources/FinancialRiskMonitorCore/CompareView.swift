import Charts
import SwiftUI

public struct CompareView: View {
    @ObservedObject private var model: AppModel
    @State private var startDate = Calendar.current.date(from: DateComponents(year: 2016, month: 9, day: 28)) ?? Date()
    @State private var endDate = Calendar.current.date(from: DateComponents(year: 2025, month: 12, day: 31)) ?? Date()
    @State private var validationMessage: String?
    public init(model: AppModel) { self.model = model }
    public var body: some View {
        Group {
            if model.featureLoading { loadingView }
            else if let error = model.comparisonError { errorView(error) }
            else if let data = model.comparison { content(data) }
        }.task { if model.comparison == nil { await model.loadComparison() } }
    }
    private var loadingView: some View { DashboardCard { HStack(spacing: 12) { ProgressView(); Text("Refreshing comparison for the selected date range…").font(.subheadline).foregroundStyle(DashboardTheme.muted) } } }
    private func errorView(_ message: String) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 8) { Label("Compare unavailable", systemImage: "exclamationmark.triangle.fill").font(.headline).foregroundStyle(DashboardTheme.risk); Text(message).font(.caption).foregroundStyle(.white); Text("The backend responded, but this screen could not decode the comparison payload.").font(.caption).foregroundStyle(DashboardTheme.muted) } } }
    private func content(_ data: CompareResponse) -> some View {
        ScrollView { VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .bottom) { VStack(alignment: .leading, spacing: 7) { Text("COMPARE ASSETS").font(.caption.weight(.bold)).tracking(1.8).foregroundStyle(DashboardTheme.primary); Text("Which asset carried more risk?").font(.title2.weight(.bold)); Text("Historical growth, volatility, and drawdown comparison.").foregroundStyle(DashboardTheme.muted) }; Spacer(); dateControls(data: data) }
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 145), spacing: 12)], spacing: 12) { ForEach([("Cumulative return", \CompareSummary.cumulativeReturnPct), ("Annualized volatility", \CompareSummary.annualizedVolatilityPct), ("Max drawdown", \CompareSummary.maxDrawdownPct)], id: \.0) { metric in paired(metric.0, key: metric.1, summaries: data.summaries, suffix: "%") }; pairedDays(data.summaries) }
            DashboardCard { VStack(alignment: .leading, spacing: 5) { Text("Normalized growth").font(.headline.weight(.bold)); Text("Both assets start at 100 • historical comparison").font(.caption).foregroundStyle(DashboardTheme.muted); Chart { ForEach(data.points) { point in LineMark(x: .value("Date", point.date), y: .value("Growth", point.normalizedGrowth), series: .value("Symbol", point.symbol)).foregroundStyle(by: .value("Symbol", point.symbol)) } }.chartForegroundStyleScale(["SPY": DashboardTheme.risk, "QQQ": DashboardTheme.primary]).chartYAxis { AxisMarks { AxisGridLine().foregroundStyle(DashboardTheme.border); AxisValueLabel().foregroundStyle(DashboardTheme.muted) } }.frame(height: 260) } }
            DashboardCard { VStack(alignment: .leading, spacing: 5) { Text("Drawdown from peak").font(.headline.weight(.bold)); Text("More negative means a larger decline").font(.caption).foregroundStyle(DashboardTheme.muted); Chart { ForEach(data.points) { point in LineMark(x: .value("Date", point.date), y: .value("Drawdown", point.drawdownPct), series: .value("Symbol", point.symbol)).foregroundStyle(by: .value("Symbol", point.symbol)) } }.chartForegroundStyleScale(["SPY": DashboardTheme.risk, "QQQ": DashboardTheme.primary]).frame(height: 210) } }
        }.padding(24) }
    }
    private func dateControls(data: CompareResponse) -> some View {
        VStack(alignment: .trailing, spacing: 8) {
            Text("Available data range: \(date(data.availableStartDate)) – \(date(data.availableEndDate))")
                .font(.caption.weight(.semibold))
                .foregroundStyle(DashboardTheme.primary)
            Text("Dates outside this range are disabled because the local dataset does not include them.")
                .font(.caption2)
                .foregroundStyle(DashboardTheme.muted)
                .multilineTextAlignment(.trailing)
            HStack(spacing: 10) {
                DatePicker("From", selection: $startDate, in: data.availableStartDate...endDate, displayedComponents: .date).labelsHidden()
                DatePicker("To", selection: $endDate, in: startDate...data.availableEndDate, displayedComponents: .date).labelsHidden()
                Button("Apply") { applyDates() }.buttonStyle(.borderedProminent)
                Button("Reset") { startDate = data.startDate; endDate = data.endDate; Task { await model.loadComparison(startDate: nil, endDate: nil) } }.buttonStyle(.bordered)
            }
            if let validationMessage { Text(validationMessage).font(.caption).foregroundStyle(DashboardTheme.risk) }
            Text("Selected window: \(date(data.startDate)) – \(date(data.endDate))").font(.caption).foregroundStyle(DashboardTheme.muted)
        }
    }
    private func applyDates() {
        guard startDate <= endDate else { validationMessage = "Start date must be on or before end date."; return }
        guard startDate >= model.comparison?.availableStartDate ?? startDate,
              endDate <= model.comparison?.availableEndDate ?? endDate else {
            let lower = model.comparison.map { date($0.availableStartDate) } ?? "2016-09-28"
            let upper = model.comparison.map { date($0.availableEndDate) } ?? "2025-12-31"
            validationMessage = "No data available for that range. Please choose dates between \(lower) and \(upper)."
            return
        }
        if let current = model.comparison, startDate == current.startDate, endDate == current.endDate { validationMessage = nil; return }
        validationMessage = nil
        Task { await model.loadComparison(startDate: startDate, endDate: endDate) }
    }
    private func paired(_ title: String, key: KeyPath<CompareSummary, Double>, summaries: [CompareSummary], suffix: String) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 10) { Text(title).font(.caption).foregroundStyle(DashboardTheme.muted); ForEach(summaries) { item in Text("\(item.symbol)  \(item[keyPath: key], specifier: "+%.1f")\(suffix)").font(.headline.weight(.bold)).foregroundStyle(item.symbol == "SPY" ? DashboardTheme.risk : DashboardTheme.primary) } } } }
    private func pairedDays(_ summaries: [CompareSummary]) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 10) { Text("Downside days").font(.caption).foregroundStyle(DashboardTheme.muted); ForEach(summaries) { item in Text("\(item.symbol)  \(item.downsideDays) days").font(.headline.weight(.bold)).foregroundStyle(item.symbol == "SPY" ? DashboardTheme.risk : DashboardTheme.primary) } } } }
    private func date(_ value: Date) -> String { value.formatted(date: .abbreviated, time: .omitted) }
}
