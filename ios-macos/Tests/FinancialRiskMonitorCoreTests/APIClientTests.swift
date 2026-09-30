import XCTest
@testable import FinancialRiskMonitorCore

final class APIClientTests: XCTestCase {
    func testEnvironmentUsesLocalBackendByDefault() {
        XCTAssertEqual(AppEnvironment().apiBaseURL.absoluteString, "http://127.0.0.1:8000")
    }
}
