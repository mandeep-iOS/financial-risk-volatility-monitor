import Foundation

public struct AppEnvironment: Sendable {
    public var apiBaseURL: URL

    public init(apiBaseURL: URL = URL(string: "http://127.0.0.1:8000")!) {
        self.apiBaseURL = apiBaseURL
    }
}
