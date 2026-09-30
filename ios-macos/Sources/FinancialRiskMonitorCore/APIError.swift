import Foundation

public enum APIError: LocalizedError, Sendable {
    case invalidResponse
    case httpStatus(Int, String?)
    case decoding(Error, String?)
    case transport(Error)

    public var errorDescription: String? {
        switch self {
        case .invalidResponse: return "The backend returned an invalid response."
        case .httpStatus(let status, let body):
            return "The backend returned HTTP \(status): \(detail(from: body) ?? "Request failed.")"
        case .decoding(let error, let body):
            let detail = body.map { " Response: \($0)" } ?? ""
            return "The app could not decode the backend response: \(decodingDescription(error)).\(detail)"
        case .transport(let error): return error.localizedDescription
        }
    }

    private func detail(from body: String?) -> String? {
        guard let body, let data = body.data(using: .utf8) else { return body }
        if let payload = try? JSONDecoder().decode([String: String].self, from: data) { return payload["detail"] }
        return body
    }

    private func decodingDescription(_ error: Error) -> String {
        guard let decodingError = error as? DecodingError else { return error.localizedDescription }
        switch decodingError {
        case .keyNotFound(let key, let context):
            return "Missing key '\(key.stringValue)' at \(context.codingPath.map(\.stringValue).joined(separator: "."))"
        case .typeMismatch(let type, let context):
            return "Type mismatch for \(type) at \(context.codingPath.map(\.stringValue).joined(separator: ".")): \(context.debugDescription)"
        case .valueNotFound(let type, let context):
            return "Missing value of type \(type) at \(context.codingPath.map(\.stringValue).joined(separator: "."))"
        case .dataCorrupted(let context):
            return "Invalid value at \(context.codingPath.map(\.stringValue).joined(separator: ".")): \(context.debugDescription)"
        @unknown default:
            return error.localizedDescription
        }
    }
}
