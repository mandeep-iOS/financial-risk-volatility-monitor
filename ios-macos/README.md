# Financial Risk Monitor SwiftUI App

This directory contains the primary iOS/macOS SwiftUI application. The Python/FastAPI service is the data science and model backend. The React app in `../frontend/` remains an optional web reference/fallback, and Streamlit remains a legacy prototype fallback.

## Open and Run in Xcode

Open `ios-macos/FinancialRiskMonitor.xcodeproj` in Xcode 27. Select the `FinancialRiskMonitorApp` scheme.

For macOS:

1. Select `My Mac` in the destination menu.
2. Press Run or `Cmd+R`.

For iOS Simulator:

1. Select `iPhone 18 Pro Max` or another installed iOS 27 simulator.
2. Press Run or `Cmd+R`.

The generated project is a real universal application target. `FinancialRiskMonitorCore` remains reusable SwiftUI/API source, while `App/FinancialRiskMonitorAppMain.swift` is the application entry point.

`Package.swift` remains available for shared code and package tests.

## Backend

Start FastAPI from the repository root:

```bash
.venv/bin/python scripts/run_api.py
```

The app defaults to `http://127.0.0.1:8000` and calls `/health` and `/symbols`. A physical iPhone cannot reach the Mac's loopback address; use the Mac's LAN IP or a hosted HTTPS API for device testing.

For a physical iPhone, use the Mac's LAN IP or a deployed HTTPS URL in `AppEnvironment`, allow the device through the firewall, and keep both devices on the same network. The iOS Simulator can use `127.0.0.1` because it runs on the Mac.

## Release Verification

```bash
cd ios-macos
swift test
xcodebuild -project FinancialRiskMonitor.xcodeproj -scheme FinancialRiskMonitorApp -destination 'platform=macOS' build
xcodebuild -project FinancialRiskMonitor.xcodeproj -scheme FinancialRiskMonitorApp -destination 'platform=iOS Simulator,name=iPhone 18 Pro Max' build

cd ..
.venv/bin/ruff check src scripts tests dashboard
MPLCONFIGDIR=.cache/matplotlib .venv/bin/pytest -q
```

## CLI verification

```bash
cd ios-macos
swift test
xcodebuild -project FinancialRiskMonitor.xcodeproj -scheme FinancialRiskMonitorApp -destination 'platform=macOS' build
xcodebuild -project FinancialRiskMonitor.xcodeproj -scheme FinancialRiskMonitorApp -destination 'platform=iOS Simulator,name=iPhone 18 Pro Max' build
```
