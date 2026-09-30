import SwiftUI

public struct ContentView: View {
    @StateObject private var model: AppModel
    @State private var selectedSection = "Overview"
    @State private var selectedSymbol = "SPY"

    private let sections = ["Overview", "Compare", "Forecast", "Model Evidence"]

    public init(model: @autoclosure @escaping () -> AppModel = AppModel()) {
        _model = StateObject(wrappedValue: model())
    }

    public var body: some View {
        NavigationSplitView {
            sidebar
        } detail: {
            dashboard
        }
        .preferredColorScheme(.dark)
        .task { await model.loadFoundation() }
    }

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 24) {
            HStack(spacing: 12) {
                Image(systemName: "chart.bar.fill").font(.title2).foregroundStyle(DashboardTheme.primary)
                Text("Financial Risk\nMonitor").font(.headline.weight(.bold))
            }
            Divider().overlay(DashboardTheme.border)
            ForEach(sections, id: \.self) { section in
                Button { selectedSection = section } label: {
                    Label(section, systemImage: icon(for: section))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 10).padding(.horizontal, 12)
                        .background(selectedSection == section ? DashboardTheme.panelRaised : .clear)
                        .clipShape(RoundedRectangle(cornerRadius: 9))
                }.buttonStyle(.plain).foregroundStyle(selectedSection == section ? .white : DashboardTheme.muted)
            }
            Spacer()
            Label(model.backendStatus, systemImage: "circle.fill").font(.caption).foregroundStyle(model.errorMessage == nil ? DashboardTheme.positive : DashboardTheme.risk)
        }
        .padding(24).frame(minWidth: 220).background(DashboardTheme.panel)
    }

    private var dashboard: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack(alignment: .bottom) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("FINANCIAL RISK ANALYTICS").font(.caption.weight(.bold)).tracking(2).foregroundStyle(DashboardTheme.primary)
                        Text(selectedSection == "Overview" ? "Financial Risk Monitor" : selectedSection).font(.largeTitle.weight(.bold))
                        Text("Analyze market risk and volatility using historical data and statistical models.").foregroundStyle(DashboardTheme.muted)
                    }
                    Spacer()
                    Picker("Asset", selection: $selectedSymbol) { ForEach(model.symbols) { Text($0.symbol).tag($0.symbol) } }.pickerStyle(.menu).frame(width: 150)
                }
                Text("Prices and models use the latest available project artifacts • Selected asset: \(selectedSymbol)").font(.caption).foregroundStyle(DashboardTheme.muted)
                if let error = model.errorMessage {
                    DashboardCard {
                        VStack(alignment: .leading, spacing: 8) {
                            Label("Backend connection failed", systemImage: "exclamationmark.triangle.fill")
                                .font(.headline.weight(.bold))
                                .foregroundStyle(DashboardTheme.risk)
                            Text(error).font(.caption).foregroundStyle(.white)
                            Text("API base URL: \(APIClient().environment.apiBaseURL.absoluteString)")
                                .font(.caption2).foregroundStyle(DashboardTheme.muted)
                            Text("Start the FastAPI server, then use Retry.")
                                .font(.caption).foregroundStyle(DashboardTheme.muted)
                            Button("Retry") { Task { await model.loadFoundation() } }
                                .buttonStyle(.borderedProminent)
                        }
                    }
                }
                if selectedSection == "Overview" { OverviewView(model: model, selectedSymbol: $selectedSymbol) }
                else if selectedSection == "Compare" { CompareView(model: model) }
                else if selectedSection == "Forecast" { ForecastView(model: model, symbol: $selectedSymbol) }
                else { EvidenceView(model: model) }
            }.padding(28)
        }
        .background(DashboardTheme.background)
        .task(id: selectedSection) {
            switch selectedSection {
            case "Compare":
                if model.comparison == nil { await model.loadComparison() }
            case "Forecast":
                await model.loadForecast(symbol: selectedSymbol)
            case "Model Evidence":
                if model.evidence == nil { await model.loadEvidence() }
            default:
                break
            }
        }
    }

    private func icon(for section: String) -> String {
        switch section { case "Overview": return "house.fill"; case "Compare": return "chart.xyaxis.line"; case "Forecast": return "chart.line.uptrend.xyaxis"; default: return "doc.text" }
    }
}
