import SwiftUI

public enum DashboardTheme {
    public static let background = Color(red: 0.027, green: 0.063, blue: 0.118)
    public static let panel = Color(red: 0.063, green: 0.114, blue: 0.188)
    public static let panelRaised = Color(red: 0.078, green: 0.157, blue: 0.255)
    public static let border = Color(red: 0.25, green: 0.51, blue: 0.78).opacity(0.32)
    public static let primary = Color(red: 0.29, green: 0.64, blue: 1.0)
    public static let risk = Color(red: 1.0, green: 0.50, blue: 0.24)
    public static let positive = Color(red: 0.30, green: 0.88, blue: 0.68)
    public static let muted = Color(red: 0.58, green: 0.67, blue: 0.77)
}

public struct DashboardCard<Content: View>: View {
    private let content: Content

    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    public var body: some View {
        content
            .padding(20)
            .background(DashboardTheme.panel)
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(DashboardTheme.border, lineWidth: 1))
            .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
