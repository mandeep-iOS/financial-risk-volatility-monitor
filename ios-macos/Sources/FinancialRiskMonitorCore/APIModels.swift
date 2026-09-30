import Foundation

public struct HealthResponse: Codable, Sendable {
    public let status: String
    public let service: String
}

public struct SymbolInfo: Codable, Identifiable, Sendable, Hashable {
    public var id: String { symbol }
    public let symbol: String
    public let name: String
    public let market: String
}
