import Foundation

public struct Freshness: Codable, Sendable {
    public let latestAvailablePriceDate: Date
    public let modelTrainingCutoff: Date
    public let forecastGeneratedAtUTC: Date
    public let forecastStartDate: Date
    public let forecastEndDate: Date
    public let forecastStatus: String
    public let isCurrent: Bool

    enum CodingKeys: String, CodingKey {
        case latestAvailablePriceDate = "latest_available_price_date"
        case modelTrainingCutoff = "model_training_cutoff"
        case forecastGeneratedAtUTC = "forecast_generated_at_utc"
        case forecastStartDate = "forecast_start_date"
        case forecastEndDate = "forecast_end_date"
        case forecastStatus = "forecast_status"
        case isCurrent = "is_current"
    }
}

public struct OverviewSummary: Codable, Sendable {
    public let latestClose: Double
    public let latestPriceDate: Date
    public let recent5dReturnPct: Double
    public let recent20dReturnPct: Double
    public let volatility20dPct: Double
    public let volatility50dPct: Double
    public let currentDrawdownPct: Double
    public let maxDrawdownPct: Double
    public let worstDailyReturnPct: Double

    enum CodingKeys: String, CodingKey {
        case latestClose = "latest_close"
        case latestPriceDate = "latest_price_date"
        case recent5dReturnPct = "recent_5d_return_pct"
        case recent20dReturnPct = "recent_20d_return_pct"
        case volatility20dPct = "volatility_20d_pct"
        case volatility50dPct = "volatility_50d_pct"
        case currentDrawdownPct = "current_drawdown_pct"
        case maxDrawdownPct = "max_drawdown_pct"
        case worstDailyReturnPct = "worst_daily_return_pct"
    }
}

public struct OverviewPoint: Codable, Identifiable, Sendable {
    public var id: Date { date }
    public let date: Date
    public let close: Double
    public let volatility20d: Double?
    public let returnPct: Double?

    enum CodingKeys: String, CodingKey {
        case date, close
        case volatility20d = "volatility_20d"
        case returnPct = "return_pct"
    }
}

public struct ScenarioItem: Codable, Identifiable, Sendable {
    public var id: String { label }
    public let label: String
    public let movePct: Double
    public let dollarImpact: Double

    enum CodingKeys: String, CodingKey {
        case label
        case movePct = "move_pct"
        case dollarImpact = "dollar_impact"
    }
}

public struct OverviewResponse: Codable, Sendable {
    public let symbol: String
    public let summary: OverviewSummary
    public let freshness: Freshness
    public let series: [OverviewPoint]
    public let scenarios: [ScenarioItem]
}
