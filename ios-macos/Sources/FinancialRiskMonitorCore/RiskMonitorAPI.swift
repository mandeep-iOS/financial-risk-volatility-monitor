import Foundation

public protocol RiskMonitorAPI: Sendable {
    func fetchHealth() async throws -> HealthResponse
    func fetchSymbols() async throws -> [SymbolInfo]
    func fetchOverview(symbol: String) async throws -> OverviewResponse
    func fetchCompare(startDate: Date?, endDate: Date?) async throws -> CompareResponse
    func fetchForecast(symbol: String, horizon: Int) async throws -> ForecastResponse
    func fetchEvidence() async throws -> EvidenceResponse
}

public struct APIClient: RiskMonitorAPI, Sendable {
    public let environment: AppEnvironment
    private let session: URLSession

    private struct ForecastRequestBody: Encodable {
        let symbol: String
        let horizon: Int
    }

    public init(environment: AppEnvironment = AppEnvironment(), session: URLSession = .shared) {
        self.environment = environment
        self.session = session
    }

    public func fetchHealth() async throws -> HealthResponse {
        try await request(path: "/health")
    }

    public func fetchSymbols() async throws -> [SymbolInfo] {
        try await request(path: "/symbols")
    }

    public func fetchOverview(symbol: String) async throws -> OverviewResponse {
        try await request(path: "/overview/\(symbol.uppercased())")
    }

    public func fetchCompare(startDate: Date? = nil, endDate: Date? = nil) async throws -> CompareResponse {
        var components = URLComponents(url: environment.apiBaseURL.appending(path: "/compare"), resolvingAgainstBaseURL: false)
        if let startDate, let endDate {
            let formatter = ISO8601DateFormatter()
            formatter.formatOptions = [.withFullDate]
            components?.queryItems = [
                URLQueryItem(name: "start_date", value: formatter.string(from: startDate)),
                URLQueryItem(name: "end_date", value: formatter.string(from: endDate))
            ]
        }
        guard let url = components?.url else { throw APIError.invalidResponse }
        return try await requestJSON(URLRequest(url: url))
    }

    public func fetchForecast(symbol: String, horizon: Int = 5) async throws -> ForecastResponse {
        var request = URLRequest(url: environment.apiBaseURL.appending(path: "/forecast"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(ForecastRequestBody(symbol: symbol.uppercased(), horizon: horizon))
        return try await requestJSON(request)
    }

    public func fetchEvidence() async throws -> EvidenceResponse {
        try await request(path: "/evidence")
    }

    private func request<Response: Decodable>(path: String) async throws -> Response {
        let url = environment.apiBaseURL.appending(path: path)
        return try await requestJSON(URLRequest(url: url))
    }

    private func requestJSON<Response: Decodable>(_ request: URLRequest) async throws -> Response {
        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else { throw APIError.invalidResponse }
            let body = String(data: data, encoding: .utf8)
            guard (200..<300).contains(httpResponse.statusCode) else {
                throw APIError.httpStatus(httpResponse.statusCode, body)
            }
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .custom { decoder in
                    let value = try decoder.singleValueContainer().decode(String.self)
                    if let date = ISO8601DateFormatter().date(from: value) { return date }
                    let formatter = DateFormatter()
                    formatter.dateFormat = "yyyy-MM-dd"
                    formatter.locale = Locale(identifier: "en_US_POSIX")
                    guard let date = formatter.date(from: value) else {
                        let container = try decoder.singleValueContainer()
                        throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid date: \(value)")
                    }
                    return date
                }
                return try decoder.decode(Response.self, from: data)
            } catch { throw APIError.decoding(error, body) }
        } catch let error as APIError {
            throw error
        } catch { throw APIError.transport(error) }
    }
}
