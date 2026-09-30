import Foundation

public struct EvidenceScore: Codable, Identifiable, Sendable {
    public var id: String { "\(symbol)-\(model)" }
    public let symbol: String
    public let model: String
    public let mae: Double
    public let maeRows: Int
    public let qlike: Double?
    public let qlikeRows: Int
    enum CodingKeys: String, CodingKey { case symbol, model, mae; case maeRows = "mae_rows"; case qlike; case qlikeRows = "qlike_rows" }
}

public struct EvidenceResponse: Codable, Sendable {
    public let evaluationStartDate: Date
    public let evaluationEndDate: Date
    public let sampleSize: Int
    public let baselineWindow: Int
    public let realizedProxy: String
    public let qlikeNote: String
    public let scores: [EvidenceScore]
    enum CodingKeys: String, CodingKey { case evaluationStartDate = "evaluation_start_date"; case evaluationEndDate = "evaluation_end_date"; case sampleSize = "sample_size"; case baselineWindow = "baseline_window"; case realizedProxy = "realized_proxy"; case qlikeNote = "qlike_note"; case scores }
}
