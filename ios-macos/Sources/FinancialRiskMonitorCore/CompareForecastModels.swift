import Foundation

public struct ComparePoint: Codable, Identifiable, Sendable {
    public var id: String { "\(symbol)-\(date.timeIntervalSince1970)" }
    public let date: Date
    public let symbol: String
    public let normalizedGrowth: Double
    public let drawdownPct: Double
    enum CodingKeys: String, CodingKey { case date, symbol; case normalizedGrowth = "normalized_growth"; case drawdownPct = "drawdown_pct" }
}

public struct CompareSummary: Codable, Identifiable, Sendable {
    public var id: String { symbol }
    public let symbol: String
    public let cumulativeReturnPct: Double
    public let annualizedVolatilityPct: Double
    public let maxDrawdownPct: Double
    public let currentDrawdownPct: Double
    public let worstDailyReturnPct: Double
    public let downsideDays: Int
    enum CodingKeys: String, CodingKey { case symbol; case cumulativeReturnPct = "cumulative_return_pct"; case annualizedVolatilityPct = "annualized_volatility_pct"; case maxDrawdownPct = "max_drawdown_pct"; case currentDrawdownPct = "current_drawdown_pct"; case worstDailyReturnPct = "worst_daily_return_pct"; case downsideDays = "downside_days" }
}

public struct CompareResponse: Codable, Sendable {
    public let startDate: Date
    public let endDate: Date
    public let availableStartDate: Date
    public let availableEndDate: Date
    public let latestAvailablePriceDate: Date
    public let points: [ComparePoint]
    public let summaries: [CompareSummary]
    enum CodingKeys: String, CodingKey { case startDate = "start_date"; case endDate = "end_date"; case availableStartDate = "available_start_date"; case availableEndDate = "available_end_date"; case latestAvailablePriceDate = "latest_available_price_date"; case points, summaries }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        startDate = try container.decode(Date.self, forKey: .startDate)
        endDate = try container.decode(Date.self, forKey: .endDate)
        latestAvailablePriceDate = try container.decode(Date.self, forKey: .latestAvailablePriceDate)
        availableStartDate = try container.decodeIfPresent(Date.self, forKey: .availableStartDate) ?? startDate
        availableEndDate = try container.decodeIfPresent(Date.self, forKey: .availableEndDate) ?? latestAvailablePriceDate
        points = try container.decode([ComparePoint].self, forKey: .points)
        summaries = try container.decode([CompareSummary].self, forKey: .summaries)
    }
}

public struct ForecastItem: Codable, Identifiable, Sendable {
    public var id: String { "\(model)-\(forecastDate.timeIntervalSince1970)" }
    public let forecastDate: Date
    public let horizon: Int
    public let model: String
    public let variancePct2: Double
    public let volatilityPct: Double
    public let trainingEndDate: Date
    enum CodingKeys: String, CodingKey { case forecastDate = "forecast_date"; case horizon, model; case variancePct2 = "variance_pct2"; case volatilityPct = "volatility_pct"; case trainingEndDate = "training_end_date" }
}

public struct ForecastResponse: Codable, Sendable {
    public let symbol: String
    public let horizon: Int
    public let varianceUnits: String
    public let volatilityUnits: String
    public let forecasts: [ForecastItem]
    public let freshness: Freshness
    enum CodingKeys: String, CodingKey { case symbol, horizon; case varianceUnits = "variance_units"; case volatilityUnits = "volatility_units"; case forecasts, freshness }
}
