import Foundation

@MainActor
public final class AppModel: ObservableObject {
    @Published public private(set) var symbols: [SymbolInfo] = []
    @Published public private(set) var isLoading = false
    @Published public private(set) var errorMessage: String?
    @Published public private(set) var backendStatus = "Connecting to API"
    @Published public private(set) var overview: OverviewResponse?
    @Published public private(set) var overviewLoading = false
    @Published public private(set) var overviewError: String?
    @Published public private(set) var comparison: CompareResponse?
    @Published public private(set) var comparisonError: String?
    @Published public private(set) var forecast: ForecastResponse?
    @Published public private(set) var forecastError: String?
    @Published public private(set) var evidence: EvidenceResponse?
    @Published public private(set) var evidenceError: String?
    @Published public private(set) var featureLoading = false
    @Published public private(set) var featureError: String?

    private let api: any RiskMonitorAPI
    private var comparisonRequestID = UUID()

    public init(api: any RiskMonitorAPI = APIClient()) {
        self.api = api
    }

    public func loadFoundation() async {
        isLoading = true
        errorMessage = nil
        do {
            async let health = api.fetchHealth()
            async let loadedSymbols = api.fetchSymbols()
            let (healthResponse, symbolResponse) = try await (health, loadedSymbols)
            backendStatus = healthResponse.status == "ok" ? "API connected" : "API unavailable"
            symbols = symbolResponse
            let symbol = symbols.first?.symbol ?? "SPY"
            await loadOverview(symbol: symbol)
            await loadComparison()
            await loadForecast(symbol: symbol)
            await loadEvidence()
        } catch {
            backendStatus = "API unavailable"
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    public func loadOverview(symbol: String) async {
        overviewLoading = true
        overviewError = nil
        do { overview = try await api.fetchOverview(symbol: symbol) }
        catch { overviewError = error.localizedDescription }
        overviewLoading = false
    }

    public func loadComparison(startDate: Date? = nil, endDate: Date? = nil) async {
        comparisonRequestID = UUID()
        let requestID = comparisonRequestID
        featureLoading = true; comparisonError = nil; comparison = nil
        do {
            let result = try await api.fetchCompare(startDate: startDate, endDate: endDate)
            guard requestID == comparisonRequestID else { return }
            comparison = result
        } catch {
            guard requestID == comparisonRequestID else { return }
            comparisonError = error.localizedDescription
        }
        featureLoading = false
    }

    public func loadForecast(symbol: String) async {
        featureLoading = true; forecastError = nil
        do { forecast = try await api.fetchForecast(symbol: symbol, horizon: 5) }
        catch { forecastError = error.localizedDescription }
        featureLoading = false
    }

    public func loadEvidence() async {
        featureLoading = true; evidenceError = nil
        do { evidence = try await api.fetchEvidence() }
        catch { evidenceError = error.localizedDescription }
        featureLoading = false
    }
}
