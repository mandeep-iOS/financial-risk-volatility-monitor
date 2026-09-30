// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "FinancialRiskMonitorApp",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [
        .library(name: "FinancialRiskMonitorCore", targets: ["FinancialRiskMonitorCore"]),
        .executable(name: "FinancialRiskMonitorMac", targets: ["FinancialRiskMonitorMac"]),
    ],
    targets: [
        .target(name: "FinancialRiskMonitorCore"),
        .executableTarget(name: "FinancialRiskMonitorMac", dependencies: ["FinancialRiskMonitorCore"]),
        .testTarget(name: "FinancialRiskMonitorCoreTests", dependencies: ["FinancialRiskMonitorCore"]),
    ]
)
